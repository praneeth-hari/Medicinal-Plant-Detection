"""
Populate plants.class_label
===========================

Links classifier class folders to ``plants`` rows, using ONLY the classes whose
identity is ``confirmed`` in docs/kb/coverage_plan.csv. Unresolved, disputed,
needs-verification and genus-level classes are never mapped.

Safety checks before a label is written:
  * the class folder exists in class_mapping.json
  * a plants row is found through the same name mapping the detection service uses
  * that row's scientific_name equals the dataset's botanical name
    (mismatches are reported and skipped, never forced)

    cd backend
    python -m scripts.populate_class_labels            # dry run (default)
    python -m scripts.populate_class_labels --apply    # write to the DB
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sqlite3
import sys

_BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_ROOT = os.path.dirname(_BACKEND)
sys.path.insert(0, _BACKEND)
sys.path.insert(0, _ROOT)

from ml.predict import map_class_name  # noqa: E402  (same mapping detection uses)

DEFAULT_CSV = os.path.join(_ROOT, "docs", "kb", "coverage_plan.csv")
DEFAULT_CLASSES = os.path.join(_BACKEND, "data", "models", "class_mapping.json")
DEFAULT_DB = os.path.join(_BACKEND, "medicinal_plants.db")


def _norm_sci(name: str) -> str:
    """'Eclipta prostrate [sic: prostrata]' -> 'eclipta prostrata'; lower-case, genus + epithet only."""
    m = re.search(r"\[sic:\s*([^\]]+)\]", name)
    base = re.sub(r"\s*\[.*?\]", "", name).strip()
    words = base.split()
    if m and words:
        words[-1] = m.group(1).strip().split()[-1]
    return " ".join(words[:2]).lower()


def plan_mappings(csv_path: str, classes_path: str, conn: sqlite3.Connection):
    classes = set(json.load(open(classes_path, encoding="utf-8")))
    rows = {r[1].lower(): r for r in conn.execute("SELECT id, common_name, scientific_name, class_label FROM plants")}
    todo, skipped = [], []
    for r in csv.DictReader(open(csv_path, encoding="utf-8")):
        folder = r["class_folder"]
        if r["identity_status"] != "confirmed":
            skipped.append((folder, f"identity_status={r['identity_status']}"))
            continue
        if folder not in classes:
            skipped.append((folder, "not in class_mapping.json"))
            continue
        row = rows.get(map_class_name(folder).lower())
        if row is None:
            skipped.append((folder, "confirmed, but no plants row yet"))
            continue
        pid, common, sci, existing = row
        if _norm_sci(sci) != _norm_sci(r["dataset_botanical_name"]):
            skipped.append((folder, f"scientific name mismatch: DB '{sci}' vs dataset '{r['dataset_botanical_name']}'"))
            continue
        if existing and existing != folder:
            skipped.append((folder, f"plants row already has class_label '{existing}'"))
            continue
        todo.append((pid, common, sci, folder, existing == folder))
    return todo, skipped


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--csv", default=DEFAULT_CSV)
    ap.add_argument("--classes", default=DEFAULT_CLASSES)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        todo, skipped = plan_mappings(args.csv, args.classes, conn)
        for pid, common, sci, folder, already in todo:
            print(f"  map  {folder:<16} -> plants#{pid} {common} ({sci}){'  [already set]' if already else ''}")
            if args.apply and not already:
                conn.execute("UPDATE plants SET class_label=? WHERE id=?", (folder, pid))
        if args.apply:
            conn.commit()
        print(f"\n{'Applied' if args.apply else 'Dry run'}: {len(todo)} mapped, {len(skipped)} left unmapped")
        for folder, why in skipped:
            print(f"  skip {folder:<24} {why}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
