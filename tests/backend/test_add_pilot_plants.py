"""
test_add_pilot_plants.py — scripts/add_pilot_plants.py plans insert-only rows for the approved pilot plants,
and (with --update) syncs existing rows without touching protected columns.
"""
import sqlite3

import pytest

from scripts import kb_render
from scripts.add_pilot_plants import PROTECTED, apply_updates, plan_inserts, plan_updates


def _conn(existing=()):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE plants (id INTEGER PRIMARY KEY, common_name TEXT, "
                 "scientific_name TEXT, class_label TEXT)")
    conn.executemany("INSERT INTO plants (common_name, scientific_name, class_label) VALUES (?, ?, ?)", existing)
    return conn


def test_plans_the_three_confirmed_plants_with_their_class_labels():
    rows, refused = plan_inserts(_conn(), kb_render.PILOT_DIR)
    assert refused == []
    got = {r["common_name"]: (r["scientific_name"], r["class_label"]) for r in rows}
    assert got == {
        "Guava": ("Psidium guajava", "Guava"),
        "Castor": ("Ricinus communis", "Castor"),
        "Tomato": ("Solanum lycopersicum", "Tomato"),
    }
    assert all(r["review_status"] == "Flagged" for r in rows)  # drafted / not yet human-reviewed
    assert all("not yet reviewed" in r["flagged_issues"].lower() for r in rows)


def test_is_insert_only_and_refuses_a_matching_existing_row():
    conn = _conn([("Guava", "Psidium guajava", None)])
    rows, refused = plan_inserts(conn, kb_render.PILOT_DIR)
    assert {r["common_name"] for r in rows} == {"Castor", "Tomato"}
    assert [label for label, _ in refused] == ["Guava"]
    assert conn.execute("SELECT count(*) FROM plants").fetchone()[0] == 1  # planning writes nothing


def test_refuses_when_class_label_is_already_taken():
    conn = _conn([("Something else", "Other species", "Tomato")])
    rows, refused = plan_inserts(conn, kb_render.PILOT_DIR)
    assert "Tomato" not in {r["class_label"] for r in rows}
    assert [label for label, _ in refused] == ["Tomato"]


def _synced_conn():
    """In-memory plants table holding the three pilot plants exactly as the serializer writes them."""
    rows, _ = plan_inserts(_conn(), kb_render.PILOT_DIR)
    cols = [*rows[0], "image_url", "created_at"]
    conn = sqlite3.connect(":memory:")
    conn.execute(f"CREATE TABLE plants (id INTEGER PRIMARY KEY, {', '.join(cols)})")
    for r in rows:
        r = {**r, "image_url": "img", "created_at": "2026-01-01"}
        conn.execute(f"INSERT INTO plants ({', '.join(r)}) VALUES ({', '.join('?' * len(r))})", list(r.values()))
    return conn


def _stale_castor(conn):
    conn.execute("UPDATE plants SET therapeutic_claims = therapeutic_claims || ' [stale]', "
                 "active_compounds = active_compounds || ' [stale]', "
                 "medicinal_uses = medicinal_uses || ' [stale]' WHERE class_label = 'Castor'")


class TestUpdateMode:
    def test_stale_castor_row_plans_exactly_the_three_differing_columns(self):
        conn = _synced_conn()
        _stale_castor(conn)
        updates, refused = plan_updates(conn, kb_render.PILOT_DIR)
        assert refused == []
        assert [(label, set(changed)) for _, label, changed in updates] == [
            ("Castor", {"therapeutic_claims", "active_compounds", "medicinal_uses"})]

    def test_identical_rows_plan_no_update(self):
        assert plan_updates(_synced_conn(), kb_render.PILOT_DIR) == ([], [])

    def test_update_leaves_protected_and_other_rows_alone_and_is_idempotent(self):
        conn = _synced_conn()
        _stale_castor(conn)
        before = conn.execute("SELECT * FROM plants WHERE class_label != 'Castor' ORDER BY id").fetchall()
        castor_before = conn.execute("SELECT id, class_label, image_url, created_at FROM plants "
                                     "WHERE class_label = 'Castor'").fetchone()
        updates, _ = plan_updates(conn, kb_render.PILOT_DIR)
        assert not PROTECTED & set(updates[0][2])
        apply_updates(conn, updates)
        assert conn.execute("SELECT * FROM plants WHERE class_label != 'Castor' ORDER BY id").fetchall() == before
        assert conn.execute("SELECT id, class_label, image_url, created_at FROM plants "
                            "WHERE class_label = 'Castor'").fetchone() == castor_before
        assert plan_updates(conn, kb_render.PILOT_DIR) == ([], [])  # a second run is a no-op

    @pytest.mark.parametrize("column, value", [("class_label", "Other"), ("scientific_name", "Other species")])
    def test_mismatched_mapping_is_refused(self, column, value):
        conn = _synced_conn()
        _stale_castor(conn)
        conn.execute(f"UPDATE plants SET {column} = ? WHERE class_label = 'Castor' OR scientific_name = 'Ricinus communis'", (value,))
        updates, refused = plan_updates(conn, kb_render.PILOT_DIR)
        assert [label for label, _ in refused] == ["Castor"] and updates == []

