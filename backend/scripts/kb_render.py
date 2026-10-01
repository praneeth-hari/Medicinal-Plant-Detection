"""
Knowledge-base pilot: validate and render
=========================================

Reads the plant files under data/knowledge_base/pilot/, checks them, and renders
section-aligned chunks. It does NOT touch the FAISS index or any production RAG code.

For each plant file it checks:
  * identity: the class_label is ``confirmed`` in docs/kb/coverage_plan.csv and its
    botanical name equals the record's scientific_name
  * the record validates as an EvidenceBasedPlant with no BLOCKING PlantValidator
    violations
  * every provenance source_id resolves in data/knowledge_base/sources.json
  * no banned phrase appears in any rendered chunk

Then it writes data/knowledge_base/pilot/pilot_chunks.json (documents / metadatas / ids,
the same three-key layout as the existing index metadata file).

    cd backend
    python -m scripts.kb_render            # validate + write pilot_chunks.json
    python -m scripts.kb_render --check    # validate only
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
_ROOT = _BACKEND.parent
sys.path.insert(0, str(_BACKEND))

from schemas.evidence_schema import BANNED_PHRASES, EvidenceBasedPlant  # noqa: E402
from schemas.plant_validator import PlantValidator, ViolationSeverity  # noqa: E402

KB_DIR = _ROOT / "data" / "knowledge_base"
PILOT_DIR = KB_DIR / "pilot"
SOURCES_PATH = KB_DIR / "sources.json"
COVERAGE_CSV = _ROOT / "docs" / "kb" / "coverage_plan.csv"
KB_VERSION = "2026.10-pilot"
MAX_CHUNK_CHARS = 900  # all-MiniLM-L6-v2 embeds ~256 tokens; keep each chunk inside that

SECTIONS = ["identity", "traditional_use", "phytochemistry", "evidence", "preparation", "safety"]
SECTION_LABEL = {
    "identity": "Identification and description",
    "traditional_use": "Traditional use",
    "phytochemistry": "Phytochemistry",
    "evidence": "Evidence for medicinal use",
    "preparation": "Preparation and dosage",
    "safety": "Safety and precautions",
}
# Existing evaluation categories (backend/data/evaluation_dataset.json) each section maps to.
SECTION_CATEGORY = {
    "identity": "identity",
    "traditional_use": "therapeutic_uses",
    "phytochemistry": "phytochemistry",
    "evidence": "therapeutic_uses",
    "preparation": "preparation",
    "safety": "safety_precautions",
}


# ── helpers ────────────────────────────────────────────────────────────────────

def _norm_sci(name: str) -> str:
    m = re.search(r"\[sic:\s*([^\]]+)\]", name)
    words = re.sub(r"\s*\[.*?\]", "", name).strip().split()
    if m and words:
        words[-1] = m.group(1).strip().split()[-1]
    return " ".join(words[:2]).lower()


def _cite(source: dict, locator: str | None) -> str:
    ids = source.get("identifiers", {})
    if "pmid" in ids and source.get("kind") != "dataset_documentation":
        first = (source.get("authors") or "").split(",")[0]
        return f"{first} et al. {source['year']}, {source['container']} (PMID {ids['pmid']})"
    if source["id"].startswith("who-v4"):
        base = source["title"].split(", in WHO")[0]
        return f"WHO monographs on selected medicinal plants, Vol. 4 (2009): {base}" + (
            f", {locator}" if locator else "")
    if source["id"].startswith("gbif"):
        return source["title"]
    return source["title"] + (f", {locator}" if locator else "")


def _fmt_num(x) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


# ── section text builders (each returns a list of item strings) ────────────────

def _items(section: str, rec: EvidenceBasedPlant, class_label: str) -> list[tuple[str, list[str]]]:
    """Item texts for a section, each with the PMIDs the record attaches to it."""
    out: list[tuple[str, list[str]]] = []
    if section == "identity":
        out.append((f"{rec.common_name} ({rec.scientific_name}), family {rec.family}.", []))
        if rec.local_names:
            out.append(("Also known as: " + ", ".join(rec.local_names) + ".", []))
        out.append((rec.description, []))
        for label, val in (("Native range", rec.native_region), ("Habitat", rec.habitat)):
            if val and not val.lower().startswith("not "):
                out.append((f"{label}: {val}", []))
        out.append((f"Image-classifier label for this plant: {class_label}.", []))
    elif section == "traditional_use":
        out.append((rec.traditional_uses_summary, []))
    elif section == "phytochemistry":
        for c in rec.active_compounds:
            out.append((f"{c.compound_name} ({c.compound_class}): {c.primary_activity} "
                        f"[evidence: {c.evidence_level.value}]", []))
    elif section == "evidence":
        out.append((rec.evidence_summary, []))
        for c in rec.therapeutic_claims:
            out.append((f"{c.condition} (evidence level: {c.evidence_level.value}). {c.claim_text}", list(c.citation_pmids)))
    elif section == "preparation":
        for m in rec.preparation_methods:
            s = f"{m.method_name}: {m.description} Plant part: {m.plant_part_used}. Intended use: {m.intended_use}."
            if m.safety_note:
                s += f" Safety note: {m.safety_note}"
            out.append((s, []))
        for d in rec.dosage_info:
            rng = (_fmt_num(d.dose_range_min) if d.dose_range_min == d.dose_range_max
                   else f"{_fmt_num(d.dose_range_min)}-{_fmt_num(d.dose_range_max)}")
            s = (f"Dose, {d.preparation_form} ({d.route}, {d.population}): {rng} {d.dose_unit}; "
                 f"{d.frequency}; maximum duration: {d.max_duration}. Source: {d.evidence_source}.")
            if d.notes:
                s += f" {d.notes}"
            out.append((s, list(d.citation_pmids)))
    elif section == "safety":
        for w in rec.safety_warnings:
            out.append((f"{w.warning_type} - {w.population}: {w.description}", list(w.citation_pmids)))
        for i in rec.drug_interactions:
            out.append((f"Drug interaction - {i.drug_name} (severity: {i.severity}): {i.interaction_description}", list(i.citation_pmids)))
        if not rec.drug_interactions:
            out.append(("Drug interactions: none were reported in the sources reviewed for this entry.", []))
        if rec.overdose_risk:
            out.append((f"Overdose: {rec.overdose_risk}", []))
    return out


def _pack(items: list[tuple[str, list[str]]], limit: int) -> list[tuple[str, set[str]]]:
    """Group items into (body, pmids) pairs of at most ``limit`` characters (an oversized item stays whole)."""
    bodies: list[tuple[str, set[str]]] = []
    cur, pm = "", set()
    for text, pmids in items:
        if cur and len(cur) + 1 + len(text) > limit:
            bodies.append((cur, pm))
            cur, pm = text, set(pmids)
        else:
            cur = cur + "\n" + text if cur else text
            pm |= set(pmids)
    if cur:
        bodies.append((cur, pm))
    return bodies


# ── per-plant processing ───────────────────────────────────────────────────────

def load_coverage(path: Path = COVERAGE_CSV) -> dict[str, dict]:
    return {r["class_folder"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}


def process_plant(path: Path, sources: dict, coverage: dict) -> tuple[list[dict], list[str], list[str]]:
    """Return (chunks, errors, notes) for one plant file."""
    errors: list[str] = []
    notes: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    label, plant_id = data["class_label"], data["plant_id"]

    # 1. identity gate
    row = coverage.get(label)
    chk = data.get("identity_check", {})
    if row is None:
        errors.append(f"class_label '{label}' not in coverage plan")
    else:
        if row["identity_status"] != "confirmed":
            errors.append(f"class_label '{label}' identity_status is '{row['identity_status']}', not confirmed")
        if _norm_sci(row["dataset_botanical_name"]) != _norm_sci(data["record"]["scientific_name"]):
            errors.append(f"scientific_name '{data['record']['scientific_name']}' does not match dataset "
                          f"'{row['dataset_botanical_name']}'")
        if str(chk.get("dataset_row")) != str(row["dataset_row"]):
            errors.append(f"identity_check.dataset_row {chk.get('dataset_row')} != coverage plan {row['dataset_row']}")

    # 2. schema + validator
    try:
        rec = EvidenceBasedPlant(**data["record"])
    except Exception as exc:  # pydantic ValidationError
        return [], errors + [f"record does not validate as EvidenceBasedPlant: {exc}"], notes
    result = PlantValidator().validate(rec)
    for v in result.violations:
        (errors if v.severity == ViolationSeverity.BLOCKING else notes).append(str(v))

    # 3. provenance
    prov = data.get("provenance", {})
    for sec, refs in prov.items():
        for ref in refs:
            if ref["source_id"] not in sources:
                errors.append(f"provenance.{sec}: unknown source_id '{ref['source_id']}'")
    for i, d in enumerate(data["record"].get("dosage_info", [])):
        for sid in d.get("source_refs", []):
            if sid not in sources:
                errors.append(f"dosage_info[{i}].source_refs: unknown source_id '{sid}'")
    if any("unknown source_id" in e for e in errors):
        return [], errors, notes  # cannot cite or render against a source that is not registered

    # 4. render
    chunks: list[dict] = []
    for sec in SECTIONS:
        items = _items(sec, rec, label)
        if not items:
            continue
        refs = prov.get(sec, [])
        if not refs:
            errors.append(f"section '{sec}' has content but no provenance")
            continue
        unused = [r["source_id"] for r in refs if r["source_id"].startswith("pmid-") and not r.get("always")
                  and not any(r["source_id"][5:] in p for _, p in items)]
        if unused:
            errors.append(f"section '{sec}': provenance lists {unused} but no item carries that PMID "
                          "(add the PMID to an item or mark the reference \"always\": true)")
        header = f"Plant: {rec.common_name} ({rec.scientific_name}) | Section: {SECTION_LABEL[sec]}"
        for body, pmids in _pack(items, MAX_CHUNK_CHARS):
            # A PMID source is cited on a chunk only if one of its items carries that PMID, or the
            # source is marked "always" in provenance; non-PMID sources (WHO, GBIF, ...) always apply.
            used = []
            for r in refs:
                pmid = sources[r["source_id"]].get("identifiers", {}).get("pmid")
                is_paper = r["source_id"].startswith("pmid-")
                if not is_paper or r.get("always") or (pmid and pmid in pmids):
                    used.append(r)
            cites = ("; ".join(_cite({**sources[r["source_id"]], "id": r["source_id"]}, r.get("locator"))
                               for r in used)
                     or "none (this statement reflects an absence of information in the sources reviewed)")
            text = "\n".join([header, body, f"Sources: {cites}"])
            chunks.append({"section": sec, "text": text, "refs": used})

    # 5. language lint on the rendered text
    for ch in chunks:
        low = ch["text"].lower()
        for phrase in BANNED_PHRASES:
            if phrase in low:
                errors.append(f"banned phrase '{phrase}' in rendered {ch['section']} chunk")

    # 6. metadata
    total = len(chunks)
    out = []
    for i, ch in enumerate(chunks):
        out.append({
            "id": f"{plant_id}-{ch['section']}-{i}",
            "document": ch["text"],
            "metadata": {
                "source": f"{plant_id}:{ch['section']}",       # keeps the existing retriever fields
                "plant": rec.common_name,
                "chunk_index": i,
                "total_chunks": total,
                "plant_id": plant_id,
                "common_name": rec.common_name,
                "scientific_name": rec.scientific_name,
                "class_label": label,
                "aliases": rec.local_names,
                "section": ch["section"],
                "category": SECTION_CATEGORY[ch["section"]],
                "overall_evidence": rec.overall_evidence_strength.value,
                "safety_class": rec.safety_class.value,
                "source_ids": [r["source_id"] for r in ch["refs"]],
                "who_monograph": rec.who_monograph_available,
                "review_status": rec.review_status.value,
                "draft_status": ("drafted / not yet human-reviewed"
                                 if any("not yet reviewed" in f.lower() for f in rec.flagged_issues)
                                 else "reviewed"),
                "last_reviewed": rec.last_reviewed,
                "kb_version": KB_VERSION,
            },
        })
    return out, errors, notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="validate only; do not write pilot_chunks.json")
    ap.add_argument("--dir", default=str(PILOT_DIR))
    args = ap.parse_args()

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
    coverage = load_coverage()
    all_chunks: list[dict] = []
    failed = False
    for path in sorted(Path(args.dir).glob("*.json")):
        if path.name == "pilot_chunks.json":
            continue
        chunks, errors, notes = process_plant(path, sources, coverage)
        status = "FAIL" if errors else "ok"
        print(f"[{status}] {path.name}: {len(chunks)} chunks, {len(errors)} blocking, {len(notes)} non-blocking")
        for e in errors:
            print(f"    BLOCKING {e}")
        for n in notes:
            print(f"    note     {n}")
        failed |= bool(errors)
        all_chunks += chunks

    if failed:
        print("\nNot writing output: fix the blocking issues above.")
        return 1
    if not args.check:
        out = {
            "kb_version": KB_VERSION,
            "documents": [c["document"] for c in all_chunks],
            "metadatas": [c["metadata"] for c in all_chunks],
            "ids": [c["id"] for c in all_chunks],
        }
        dest = Path(args.dir) / "pilot_chunks.json"
        dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nWrote {len(all_chunks)} chunks to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
