"""
Add the approved pilot plants to the ``plants`` table
=====================================================

Inserts Guava, Castor and Tomato from data/knowledge_base/pilot/ using the existing
EvidenceBasedPlant -> column converter (utils.plant_serializer.evidence_to_db_fields),
plus the plant's confirmed ``class_label``.

By default it is insert-only: it never updates an existing row, and refuses (for that
plant) if a row with the same scientific name, common name or class_label already exists.
With --update it instead synchronises an existing row from the current plant record: the row
must match on BOTH scientific_name and class_label, only serializer-backed columns whose
values differ are written, and id, class_label, image_url and created_at are never touched.
Both modes refuse any plant that fails the pilot gates in scripts.kb_render (confirmed
identity in docs/kb/coverage_plan.csv, no BLOCKING validator violations, registered sources).

    cd backend
    python -m scripts.add_pilot_plants                    # insert, dry run (default)
    python -m scripts.add_pilot_plants --apply            # insert into the DB
    python -m scripts.add_pilot_plants --update           # sync existing rows, dry run
    python -m scripts.add_pilot_plants --update --apply   # sync existing rows in the DB
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND))

from schemas.evidence_schema import EvidenceBasedPlant  # noqa: E402
from scripts import kb_render  # noqa: E402
from utils.plant_serializer import evidence_to_db_fields  # noqa: E402

DEFAULT_DB = _BACKEND / "medicinal_plants.db"
PROTECTED = {"id", "class_label", "image_url", "created_at"}  # never written in --update mode


def _gated_plants(pilot_dir: Path):
    """Return ([(class_label, record)] for plants passing the pilot gates, refusals)."""
    sources = json.loads(kb_render.SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
    coverage = kb_render.load_coverage()
    plants, refused = [], []
    for path in sorted(pilot_dir.glob("*.json")):
        if path.name == "pilot_chunks.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        label = data["class_label"]
        _, errors, _ = kb_render.process_plant(path, sources, coverage)
        if errors:
            refused.append((label, "pilot gates failed: " + "; ".join(errors)))
            continue
        plants.append((label, EvidenceBasedPlant(**data["record"])))
    return plants, refused


def plan_inserts(conn: sqlite3.Connection, pilot_dir: Path):
    """Return (rows_to_insert, refusals). Each row is a dict of column -> value."""
    plants, refused = _gated_plants(pilot_dir)
    rows = []
    for label, rec in plants:
        existing = conn.execute(
            "SELECT id, common_name, scientific_name, class_label FROM plants "
            "WHERE lower(scientific_name)=lower(?) OR lower(common_name)=lower(?) OR class_label=?",
            (rec.scientific_name, rec.common_name, label)).fetchall()
        if existing:
            refused.append((label, f"a matching plants row already exists: {existing}"))
            continue
        fields = evidence_to_db_fields(rec)
        fields["class_label"] = label
        rows.append(fields)
    return rows, refused


def plan_updates(conn: sqlite3.Connection, pilot_dir: Path):
    """Return (updates, refusals). Each update is (id, class_label, {column: new_value}) holding only
    the serializer-backed columns whose stored value differs from the current record."""
    plants, refused = _gated_plants(pilot_dir)
    updates = []
    for label, rec in plants:
        cur = conn.execute(
            "SELECT * FROM plants WHERE lower(scientific_name)=lower(?) OR class_label=?",
            (rec.scientific_name, label))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        if not rows:
            refused.append((label, "no existing plants row (run without --update to insert)"))
            continue
        if len(rows) != 1 or rows[0]["class_label"] != label or rows[0]["scientific_name"].lower() != rec.scientific_name.lower():
            refused.append((label, "scientific_name and class_label do not both match one plants row: "
                                   f"{[(r['id'], r['scientific_name'], r['class_label']) for r in rows]}"))
            continue
        changed = {k: v for k, v in evidence_to_db_fields(rec).items()
                   if k not in PROTECTED and rows[0][k] != v}
        if changed:
            updates.append((rows[0]["id"], label, changed))
    return updates, refused


def apply_updates(conn: sqlite3.Connection, updates) -> None:
    for plant_id, _, changed in updates:
        conn.execute(f"UPDATE plants SET {', '.join(f'{c}=?' for c in changed)} WHERE id=?",
                     [*changed.values(), plant_id])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--update", action="store_true", help="sync existing rows instead of inserting new ones")
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--dir", default=str(kb_render.PILOT_DIR))
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        if args.update:
            todo, refused = plan_updates(conn, Path(args.dir))
            for _, label, changed in todo:
                print(f"  update {label}: {', '.join(changed)}")
            if args.apply:
                apply_updates(conn, todo)
        else:
            todo, refused = plan_inserts(conn, Path(args.dir))
            for f in todo:
                print(f"  insert {f['common_name']:<8} {f['scientific_name']:<22} {f['family']:<14} "
                      f"class_label={f['class_label']}  review_status={f['review_status']}")
                if args.apply:
                    cols = list(f)
                    conn.execute(f"INSERT INTO plants ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
                                 [f[c] for c in cols])
        if args.apply:
            conn.commit()
        for label, why in refused:
            print(f"  REFUSED {label}: {why}")
        print(f"\n{'Applied' if args.apply else 'Dry run'}: {len(todo)} to {'update' if args.update else 'insert'}, "
              f"{len(refused)} refused")
        return 1 if refused else 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
