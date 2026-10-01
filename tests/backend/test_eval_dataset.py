"""
test_eval_dataset.py — the expanded retrieval evaluation set (backend/data/evaluation_dataset.json).

The first 40 questions are the original baseline and must stay as they were. The pilot questions must be
answerable from the verified pilot chunks, and their declared wording style must match the wording.
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = json.loads((ROOT / "backend" / "data" / "evaluation_dataset.json").read_text(encoding="utf-8"))["questions"]
CHUNKS = json.loads((ROOT / "data" / "knowledge_base" / "pilot" / "pilot_chunks.json").read_text(encoding="utf-8"))
ORIGINAL, PILOT = QUESTIONS[:40], QUESTIONS[40:]


def test_original_forty_are_unchanged_in_shape_and_order():
    assert len(ORIGINAL) == 40
    assert all(set(q) == {"plant", "question", "category"} for q in ORIGINAL)
    assert [q["plant"] for q in ORIGINAL[:3]] == ["Tulsi", "Tulsi", "Neem"]
    assert ORIGINAL[-1]["plant"] == "Fenugreek"
    assert len({q["plant"] for q in ORIGINAL}) == 20


def test_pilot_questions_cover_the_three_plants_and_every_applicable_category():
    assert all(q["set"] == "pilot" for q in PILOT)
    by_plant = Counter(q["plant"] for q in PILOT)
    assert set(by_plant) == {"Guava", "Castor", "Tomato"} and min(by_plant.values()) >= 10
    cats = {(q["plant"], q["category"]) for q in PILOT}
    for plant in ("Guava", "Castor", "Tomato"):
        for cat in ("identity", "therapeutic_uses", "phytochemistry", "safety_precautions"):
            assert (plant, cat) in cats
    assert ("Guava", "preparation") in cats and ("Castor", "preparation") in cats
    assert ("Tomato", "preparation") not in cats  # the tomato entry has no preparation section
    assert sum(q["category"] == "safety_precautions" for q in PILOT) >= 18


def test_no_duplicate_questions():
    texts = [q["question"] for q in QUESTIONS]
    assert len(texts) == len(set(texts))


def test_pilot_questions_are_answerable_from_the_pilot_chunks():
    for q in PILOT:
        hits = [d for d, m in zip(CHUNKS["documents"], CHUNKS["metadatas"])
                if m["plant"] == q["plant"] and m["category"] == q["category"]
                and all(a.lower() in d.lower() for a in q["answer_contains"])]
        assert hits, q["question"]


def test_declared_style_matches_the_wording_and_some_questions_omit_the_name():
    names = {}
    for m in CHUNKS["metadatas"]:
        names[m["plant"]] = (m["common_name"].lower(), m["scientific_name"].lower(), [a.lower() for a in m["aliases"]])
    for q in PILOT:
        common, sci, aliases = names[q["plant"]]
        ql = q["question"].lower()
        has_common, has_other = common in ql, sci in ql or any(a in ql for a in aliases)
        if q["style"] == "common_name":
            assert has_common
        elif q["style"] == "alias_or_scientific":
            assert has_other and not has_common
        else:
            assert q["style"] == "descriptor" and not has_common and not has_other
    assert sum(q["style"] != "common_name" for q in PILOT) >= 20
