"""
test_dosage_source_refs.py — DosageInfo.source_refs: a clinical-trial dose may be backed by an
authoritative non-PubMed source (e.g. a WHO monograph) instead of a PMID (rule R-07).
"""
import json

from schemas.evidence_schema import DosageInfo, EvidenceBasedPlant
from schemas.plant_validator import PlantValidator
from scripts import kb_render


def _dose(**kw):
    base = dict(preparation_form="Capsule", plant_part="Leaf", route="Oral", population="Adults",
                dose_range_min=500, dose_range_max=500, dose_unit="mg", is_clinical_trial_dose=True)
    return DosageInfo(**{**base, **kw})


def _plant(dose):
    rec = json.loads((kb_render.PILOT_DIR / "guava.json").read_text(encoding="utf-8"))["record"]
    rec["dosage_info"] = [dose.model_dump()]
    return EvidenceBasedPlant(**rec)


def _r07(plant):
    return [v for v in PlantValidator().validate(plant).violations if v.rule_id == "R-07"]


def test_source_refs_defaults_to_empty_and_old_records_still_parse():
    d = DosageInfo.model_validate({"preparation_form": "Tea", "plant_part": "Leaf",
                                   "route": "Oral", "population": "Adults"})
    assert d.source_refs == []


def test_trial_dose_with_no_pmid_and_no_source_is_still_blocked():
    v = _r07(_plant(_dose()))
    assert len(v) == 1 and v[0].severity.value == "BLOCKING"


def test_trial_dose_with_pmid_passes():
    assert _r07(_plant(_dose(citation_pmids=["12413703"]))) == []


def test_trial_dose_with_authoritative_source_ref_passes_without_inventing_a_pmid():
    d = _dose(source_refs=["who-v4-guavae"])
    assert d.citation_pmids == []
    assert _r07(_plant(d)) == []


def test_guava_doses_are_trial_doses_backed_by_who_not_by_a_pmid():
    rec = json.loads((kb_render.PILOT_DIR / "guava.json").read_text(encoding="utf-8"))["record"]
    assert rec["dosage_info"] and all(d["is_clinical_trial_dose"] for d in rec["dosage_info"])
    assert all(d["source_refs"] == ["who-v4-guavae"] and d["citation_pmids"] == [] for d in rec["dosage_info"])


def test_castor_laxative_dose_is_not_marked_as_a_trial_dose():
    rec = json.loads((kb_render.PILOT_DIR / "castor.json").read_text(encoding="utf-8"))["record"]
    assert all(not d["is_clinical_trial_dose"] for d in rec["dosage_info"])


def test_unknown_dosage_source_ref_is_rejected(tmp_path):
    data = json.loads((kb_render.PILOT_DIR / "guava.json").read_text(encoding="utf-8"))
    data["record"]["dosage_info"][0]["source_refs"] = ["who-v4-does-not-exist"]
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    sources = json.loads(kb_render.SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
    _, errors, _ = kb_render.process_plant(bad, sources, kb_render.load_coverage())
    assert any("source_refs" in e for e in errors)
