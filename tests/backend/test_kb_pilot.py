"""
test_kb_pilot.py — the Guava / Castor / Tomato knowledge-base pilot (data/knowledge_base/pilot/).

Checks that every pilot plant passes the identity gate, validates as an EvidenceBasedPlant with no
BLOCKING PlantValidator violations, cites only registered sources, and that the committed
pilot_chunks.json matches what the renderer produces from the plant files.
"""
import json
from pathlib import Path

import pytest

from scripts import kb_render

PLANT_FILES = sorted(p for p in kb_render.PILOT_DIR.glob("*.json") if p.name != "pilot_chunks.json")
SOURCES = json.loads(kb_render.SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
COVERAGE = kb_render.load_coverage()


def test_pilot_covers_the_three_plants():
    assert {p.stem for p in PLANT_FILES} == {"guava", "castor", "tomato"}


@pytest.mark.parametrize("path", PLANT_FILES, ids=lambda p: p.stem)
def test_plant_passes_all_gates(path):
    chunks, errors, _ = kb_render.process_plant(path, SOURCES, COVERAGE)
    assert errors == []
    assert chunks, "plant rendered no chunks"
    assert all(len(c["document"]) < 1500 for c in chunks)
    for c in chunks:
        m = c["metadata"]
        assert m["class_label"] and m["plant_id"] and m["section"] and m["source_ids"] is not None
        assert c["document"].startswith(f"Plant: {m['common_name']} ({m['scientific_name']}) | Section:")
        assert "\nSources: " in c["document"]


def test_only_confirmed_identities_are_used():
    for path in PLANT_FILES:
        label = json.loads(path.read_text(encoding="utf-8"))["class_label"]
        assert COVERAGE[label]["identity_status"] == "confirmed"


def test_identity_gate_blocks_unconfirmed_class(tmp_path):
    data = json.loads((kb_render.PILOT_DIR / "guava.json").read_text(encoding="utf-8"))
    data["class_label"] = "Kambajala"  # unresolved in the coverage plan
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    _, errors, _ = kb_render.process_plant(bad, SOURCES, COVERAGE)
    assert any("not confirmed" in e for e in errors)


def test_unknown_source_id_is_rejected(tmp_path):
    data = json.loads((kb_render.PILOT_DIR / "tomato.json").read_text(encoding="utf-8"))
    data["provenance"]["safety"].append({"source_id": "pmid-00000000"})
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    _, errors, _ = kb_render.process_plant(bad, SOURCES, COVERAGE)
    assert any("unknown source_id" in e for e in errors)


def test_committed_chunks_are_up_to_date():
    committed = json.loads((kb_render.PILOT_DIR / "pilot_chunks.json").read_text(encoding="utf-8"))
    rendered = []
    for path in PLANT_FILES:
        chunks, errors, _ = kb_render.process_plant(path, SOURCES, COVERAGE)
        assert errors == []
        rendered += chunks
    assert committed["ids"] == [c["id"] for c in rendered]
    assert committed["documents"] == [c["document"] for c in rendered]
    assert committed["metadatas"] == [c["metadata"] for c in rendered]


def test_castor_entry_does_not_extend_oil_monograph_to_leaf():
    castor = json.loads((kb_render.PILOT_DIR / "castor.json").read_text(encoding="utf-8"))["record"]
    assert "covers only the fixed oil" in castor["description"].lower()
    assert any("poisonous" in w["description"].lower() for w in castor["safety_warnings"])


def test_castor_seed_notice_is_first_and_leaf_is_not_called_poisonous():
    castor = json.loads((kb_render.PILOT_DIR / "castor.json").read_text(encoding="utf-8"))["record"]
    first = castor["safety_warnings"][0]
    text = first["description"].lower()
    assert first["description"].startswith("SAFETY NOTICE:")
    assert "seeds are poisonous" in text and "ricin" in text
    leaf = castor["safety_warnings"][1]
    assert leaf["warning_type"] == "Advisory"
    assert "establish the leaf neither as poisonous nor as safe" in leaf["description"].lower()
    assert "not a statement about seed toxicity or leaf toxicity" in leaf["description"].lower()
    assert "leaf" in castor["description"].lower() and "poisonous or as safe" in castor["description"].lower()


def test_pilot_plants_are_marked_not_reviewed():
    for path in PLANT_FILES:
        rec = json.loads(path.read_text(encoding="utf-8"))["record"]
        assert any("not yet reviewed" in f.lower() for f in rec["flagged_issues"])
