"""
test_class_label.py — plants.class_label (classifier-label link) and its populate script.
"""
import csv
import json
import sqlite3

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Base
from models.plant import Plant
from scripts.populate_class_labels import plan_mappings


@pytest.fixture
def session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'labels.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


class TestClassLabelColumn:
    def test_nullable_and_repeatable_nulls(self, session):
        session.add_all([
            Plant(common_name="A", scientific_name="Genus a"),
            Plant(common_name="B", scientific_name="Genus b"),
        ])
        session.commit()  # two NULL labels must not collide
        assert [p.class_label for p in session.query(Plant).all()] == [None, None]

    def test_label_must_be_unique(self, session):
        session.add_all([
            Plant(common_name="A", scientific_name="Genus a", class_label="Folder"),
            Plant(common_name="B", scientific_name="Genus b", class_label="Folder"),
        ])
        with pytest.raises(IntegrityError):
            session.commit()


class TestPopulatePlan:
    def _setup(self, tmp_path, rows, classes):
        csv_path = tmp_path / "plan.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["class_folder", "identity_status", "dataset_botanical_name"])
            w.writeheader()
            w.writerows(rows)
        classes_path = tmp_path / "classes.json"
        classes_path.write_text(json.dumps(classes))
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE plants (id INTEGER PRIMARY KEY, common_name TEXT, "
                     "scientific_name TEXT, class_label TEXT)")
        conn.executemany("INSERT INTO plants (common_name, scientific_name) VALUES (?, ?)", [
            ("Tulsi", "Ocimum tenuiflorum"), ("Mint", "Mentha spicata"),
            ("Neem", "Azadirachta indica"), ("Ginger", "Zingiber officinale")])
        return str(csv_path), str(classes_path), conn

    def test_only_confirmed_classes_are_mapped(self, tmp_path):
        rows = [
            {"class_folder": "Tulsi", "identity_status": "confirmed", "dataset_botanical_name": "Ocimum tenuiflorum"},
            {"class_folder": "Mint", "identity_status": "genus_level_only", "dataset_botanical_name": "Mentha"},
            {"class_folder": "Ginger", "identity_status": "unresolved", "dataset_botanical_name": "Zingiber officinale"},
        ]
        todo, skipped = plan_mappings(*self._setup(tmp_path, rows, ["Tulsi", "Mint", "Ginger"]))
        assert [t[3] for t in todo] == ["Tulsi"]
        assert {s[0] for s in skipped} == {"Mint", "Ginger"}

    def test_scientific_name_mismatch_is_skipped(self, tmp_path):
        rows = [{"class_folder": "Neem", "identity_status": "confirmed",
                 "dataset_botanical_name": "Melia azedarach"}]
        todo, skipped = plan_mappings(*self._setup(tmp_path, rows, ["Neem"]))
        assert todo == [] and "mismatch" in skipped[0][1]

    def test_sic_correction_and_missing_row(self, tmp_path):
        rows = [{"class_folder": "Guava", "identity_status": "confirmed",
                 "dataset_botanical_name": "Psidium guajava"}]
        todo, skipped = plan_mappings(*self._setup(tmp_path, rows, ["Guava"]))
        assert todo == [] and "no plants row" in skipped[0][1]
