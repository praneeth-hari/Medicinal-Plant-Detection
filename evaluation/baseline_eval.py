"""
baseline_eval.py -- read-only baseline evaluation
============================================================
Measures the CURRENT saved classifier and RAG index. It trains nothing, rebuilds
nothing and does not modify production code or data.

    python evaluation/baseline_eval.py              # everything
    python evaluation/baseline_eval.py --skip-rag   # classifier + data audit only
    python evaluation/baseline_eval.py --skip-cls   # RAG only

Outputs (evaluation/reports/):
    baseline_report.json   machine-readable, for comparing future runs
    baseline_report.md     human-readable summary
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
DATA = ROOT / "data"
MODELS = BACKEND / "data" / "models"
EVAL_SET = BACKEND / "data" / "evaluation_dataset.json"
EMBED_DIR = BACKEND / "data" / "embeddings"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
SPLITS = ("train", "val", "test")
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))

# Which section header in a chunk's text identifies each evaluation category.
CATEGORY_HEADERS = {
    "therapeutic_uses": "Medicinal Uses:",
    "preparation": "Preparation Methods:",
    "safety_precautions": "Precautions:",
    "misconceptions": "Common Misconceptions:",
}
KS = (1, 3, 5)


# ============================================================
# 1. RAG retrieval
# ============================================================
def _chunk_has_category(text: str, category: str, meta: dict | None = None) -> bool:
    # Chunks built by the KB renderer carry an explicit "category" in their metadata; the original
    # hand-written chunks do not, so they are matched by the section header in their text.
    if meta and meta.get("category"):
        return meta["category"] == category
    header = CATEGORY_HEADERS.get(category)
    return header is not None and header in text


def _score_ranking(question: dict, docs: list[dict]) -> dict:
    """Per-question hit flags for the ranked list ``docs``."""
    plant = question["plant"].strip().lower()
    cat = question["category"]
    needles = [a.lower() for a in question.get("answer_contains", [])]
    plant_rank = cat_rank = ans_rank = None
    for rank, d in enumerate(docs, 1):
        same_plant = str(d["metadata"].get("plant", "")).strip().lower() == plant
        if same_plant and plant_rank is None:
            plant_rank = rank
        in_cat = same_plant and _chunk_has_category(d["document"], cat, d["metadata"])
        if in_cat and cat_rank is None:
            cat_rank = rank
        # answer-bearing chunk: right plant, right category, and it contains every required phrase
        if needles and in_cat and ans_rank is None and all(n in d["document"].lower() for n in needles):
            ans_rank = rank
    return {
        "plant_rank": plant_rank,
        "plant_category_rank": cat_rank,
        "answer_rank": ans_rank,
        "has_answer_key": bool(needles),
        "top1_plant": docs[0]["metadata"].get("plant") if docs else None,
        "top5": [f'{d["metadata"].get("plant")}#{d["metadata"].get("chunk_index")}' for d in docs],
    }


def _summarise(rows: list[dict], key: str) -> dict:
    n = len(rows)
    return {f"hit@{k}": round(sum(1 for r in rows if r[key] is not None and r[key] <= k) / n, 4)
            for k in KS}


def _group_metrics(rows: list[dict]) -> dict:
    keyed = [r for r in rows if r["has_answer_key"]]
    m = {
        "n": len(rows),
        "plant_match": _summarise(rows, "plant_rank"),
        "plant_and_category_match": _summarise(rows, "plant_category_rank"),
        "top1_wrong_plant": sum(1 for r in rows if r["top1_plant"] != r["plant"]),
    }
    if keyed:
        m["answer_chunk_match"] = {"n": len(keyed), **_summarise(keyed, "answer_rank")}
    return m


def _by_set(all_rows: list[dict]) -> dict:
    groups = {"original": [r for r in all_rows if r["set"] == "original"],
              "pilot": [r for r in all_rows if r["set"] == "pilot"],
              "combined": all_rows}
    out = {}
    for gname, rows in groups.items():
        if not rows:
            continue
        g = _group_metrics(rows)
        g["by_category"] = {c: _group_metrics([r for r in rows if r["category"] == c])
                            for c in sorted({r["category"] for r in rows})}
        g["by_plant"] = {p: _group_metrics([r for r in rows if r["plant"] == p])
                         for p in sorted({r["plant"] for r in rows})}
        styles = sorted({r["style"] for r in rows if r["style"]})
        if styles:
            g["by_style"] = {st: _group_metrics([r for r in rows if r["style"] == st]) for st in styles}
        g["misses_at_5_plant_and_category"] = [
            {k: r[k] for k in ("plant", "category", "question", "top5")}
            for r in rows if r["plant_category_rank"] is None]
        g["misses_at_5_answer_chunk"] = [
            {k: r[k] for k in ("plant", "category", "question", "top5")}
            for r in rows if r["has_answer_key"] and r["answer_rank"] is None]
        out[gname] = g
    return out


def evaluate_rag() -> dict:
    from rag.embeddings import EmbeddingService
    from rag.retriever import DocumentRetriever
    from rag.vector_store import VectorStoreService

    questions = json.loads(EVAL_SET.read_text(encoding="utf-8"))["questions"]
    store = VectorStoreService(str(EMBED_DIR), "medicinal_plants")
    if not store.load_index():
        raise SystemExit(f"Could not load FAISS index from {EMBED_DIR}")
    emb = EmbeddingService("all-MiniLM-L6-v2")
    retriever = DocumentRetriever(store, emb)

    kb_plants = sorted({str(m.get("plant")) for m in store._metadatas})
    out = {
        "n_questions": len(questions),
        "n_original_questions": sum(1 for q in questions if q.get("set", "original") == "original"),
        "n_pilot_questions": sum(1 for q in questions if q.get("set") == "pilot"),
        "n_chunks": store.count,
        "kb_plants": kb_plants,
        "category_counts": dict(Counter(q["category"] for q in questions)),
    }
    pipelines = {
        # exactly what the app calls: embed -> FAISS top-10 -> name boost -> per-plant cap
        "production_retriever": lambda q: retriever.retrieve(q, top_k=5),
        # embedding + FAISS only, no keyword boost / dedupe (shows what the boost adds)
        "raw_faiss": lambda q: store.search(emb.embed_text(q), n_results=5),
    }
    for name, fn in pipelines.items():
        all_rows = []
        for q in questions:
            r = _score_ranking(q, fn(q["question"]))
            r.update(plant=q["plant"], category=q["category"], question=q["question"],
                     set=q.get("set", "original"), style=q.get("style"))
            all_rows.append(r)
        # The legacy keys below are computed over the ORIGINAL questions only, exactly as in the
        # first baseline, so they stay directly comparable. Everything else is under "by_set".
        rows = [r for r in all_rows if r["set"] == "original"]
        by_cat = {}
        for cat in sorted({r["category"] for r in rows}):
            sub = [r for r in rows if r["category"] == cat]
            by_cat[cat] = {"n": len(sub), **_summarise(sub, "plant_category_rank")}
        out[name] = {
            "by_set": _by_set(all_rows),
            "plant_match": _summarise(rows, "plant_rank"),
            "plant_and_category_match": _summarise(rows, "plant_category_rank"),
            "top1_wrong_plant": sum(1 for r in rows if r["top1_plant"] != r["plant"]),
            "by_category_plant_and_category": by_cat,
            "misses_at_5_plant_and_category": [
                {k: r[k] for k in ("plant", "category", "question", "top5")}
                for r in rows if r["plant_category_rank"] is None],
        }
    return out


# ============================================================
# 2. Classifier
# ============================================================
def evaluate_classifier() -> dict:
    import torch
    from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms

    from ml.augment import BackgroundSwap
    from ml.model import PlantClassifier
    from ml.predict import map_class_name

    classes = json.loads((MODELS / "class_mapping.json").read_text(encoding="utf-8"))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PlantClassifier.load_checkpoint(str(MODELS / "plant_classifier.pth"),
                                            num_classes=len(classes)).to(device).eval()
    norm = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    plain = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), norm])

    def run(split: str, shifted: bool = False):
        tf = plain
        if shifted:  # same protocol as train.py "shifted" eval: every photo gets a new background
            random_state = (np.random.get_state(), random.getstate())
            random.seed(1234)
            np.random.seed(1234)
            tf = transforms.Compose([transforms.Resize((224, 224)),
                                     BackgroundSwap(str(DATA / "train"), p=1.0, seed=1234),
                                     transforms.ToTensor(), norm])
        ds = datasets.ImageFolder(str(DATA / split), transform=tf)
        assert ds.classes == classes, "class_mapping.json does not match data folders"
        preds, labels, confs = [], [], []
        with torch.no_grad():
            for x, y in DataLoader(ds, batch_size=32, shuffle=False, num_workers=0):
                p = torch.softmax(model(x.to(device)), 1).cpu()
                c, idx = p.max(1)
                preds += idx.tolist(); labels += y.tolist(); confs += c.tolist()
        if shifted:
            np.random.set_state(random_state[0]); random.setstate(random_state[1])
        return ds, np.array(preds), np.array(labels), np.array(confs)

    def metrics(labels, preds):
        p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="macro", zero_division=0)
        return {"n": int(len(labels)), "accuracy": round(float((labels == preds).mean()), 4),
                "macro_precision": round(float(p), 4), "macro_recall": round(float(r), 4),
                "macro_f1": round(float(f1), 4)}

    t0 = time.time()
    res: dict = {"device": str(device), "n_classes": len(classes)}
    ds_test, p_test, y_test, c_test = run("test")
    _, p_val, y_val, _ = run("val")
    _, p_tsh, y_tsh, _ = run("test", shifted=True)
    res["test"] = metrics(y_test, p_test)
    res["val"] = metrics(y_val, p_val)
    res["test_background_swapped"] = metrics(y_tsh, p_tsh)
    res["mean_confidence_correct"] = round(float(c_test[p_test == y_test].mean()), 4)
    res["mean_confidence_wrong"] = round(float(c_test[p_test != y_test].mean()), 4) \
        if (p_test != y_test).any() else None

    # per-class accuracy on pooled held-out (val + test) -> ~2x the samples per class
    y_all = np.concatenate([y_val, y_test]); p_all = np.concatenate([p_val, p_test])
    per_class = []
    for i, name in enumerate(classes):
        m = y_all == i
        mt = y_test == i
        ms = y_tsh == i
        per_class.append({
            "class": name,
            "n_heldout": int(m.sum()),
            "acc_heldout": round(float((p_all[m] == i).mean()), 4) if m.any() else None,
            "n_test": int(mt.sum()),
            "acc_test": round(float((p_test[mt] == i).mean()), 4) if mt.any() else None,
            "acc_test_bg_swapped": round(float((p_tsh[ms] == i).mean()), 4) if ms.any() else None,
            "n_train": len(list((DATA / "train" / name).iterdir())),
        })
    per_class.sort(key=lambda r: (r["acc_heldout"], r["class"]))
    res["per_class"] = per_class
    cm = confusion_matrix(y_all, p_all, labels=range(len(classes)))
    np.fill_diagonal(cm, 0)
    confused = sorted(((int(cm[i, j]), classes[i], classes[j])
                       for i in range(len(classes)) for j in range(len(classes)) if cm[i, j]),
                      reverse=True)[:10]
    res["top_confusions_heldout"] = [{"count": c, "true": a, "predicted": b} for c, a, b in confused]
    res["classes_below_90pct_heldout"] = [r["class"] for r in per_class if (r["acc_heldout"] or 0) < 0.9]

    # which classifier classes does the RAG knowledge base know about?
    meta = json.loads((EMBED_DIR / "medicinal_plants_meta.json").read_text(encoding="utf-8"))
    kb = {m["plant"].lower() for m in meta["metadatas"]}
    covered = [c for c in classes if map_class_name(c).lower() in kb]
    res["rag_coverage_of_classifier_classes"] = {
        "classes": len(classes), "with_kb_chunks": len(covered), "covered": covered}
    res["eval_seconds"] = round(time.time() - t0, 1)
    res["_test_ds_samples"] = [(Path(p).as_posix(), int(l)) for p, l in ds_test.samples]
    res["_test_correct"] = (p_test == y_test).tolist()
    return res


# ============================================================
# 3. Leakage / duplicate audit
# ============================================================
def _dhash(path: Path) -> tuple[int, str]:
    """64-bit difference hash + md5 of the file bytes."""
    import hashlib
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    with Image.open(path) as im:
        im.draft("L", (64, 64))
        g = np.asarray(im.convert("L").resize((9, 8), Image.LANCZOS), dtype=np.int16)
    bits = (g[:, 1:] > g[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2), md5


_POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def _hamming_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """a: (n,8) uint8, b: (m,8) uint8 -> (n,m) hamming distances."""
    out = np.empty((len(a), len(b)), dtype=np.uint8)
    for i in range(len(a)):
        out[i] = _POP[np.bitwise_xor(a[i], b)].sum(1)
    return out


_TS = re.compile(r"(?:img|p)_(\d{8})_(\d{6})", re.I)
_NUM = re.compile(r"^(\d+)\.\w+$")


def audit_leakage(test_correct: list[bool] | None, test_samples: list | None) -> dict:
    items = []  # (split, class, path)
    for s in SPLITS:
        for cdir in sorted((DATA / s).iterdir()):
            if cdir.is_dir():
                items += [(s, cdir.name, f) for f in sorted(cdir.iterdir()) if f.suffix.lower() in IMG_EXT]
    hashes, md5s = [], []
    for _, _, f in items:
        try:
            h, m = _dhash(f)
        except Exception:
            h, m = 0, "unreadable:" + f.name
        hashes.append(np.frombuffer(h.to_bytes(8, "big"), dtype=np.uint8)); md5s.append(m)
    H = np.stack(hashes)
    split = np.array([i[0] for i in items]); cls = np.array([i[1] for i in items])
    res: dict = {"n_images": len(items)}

    # exact byte-identical duplicates
    groups = defaultdict(list)
    for idx, m in enumerate(md5s):
        groups[m].append(idx)
    dup = [g for g in groups.values() if len(g) > 1]
    res["exact_duplicate_groups"] = len(dup)
    res["exact_duplicates_across_splits"] = sum(1 for g in dup if len({split[i] for i in g}) > 1)
    res["exact_duplicates_across_classes"] = sum(1 for g in dup if len({cls[i] for i in g}) > 1)

    # near duplicates: nearest TRAIN neighbour of every val/test image
    tr = np.where(split == "train")[0]
    nearest = {}
    for s in ("val", "test"):
        idx = np.where(split == s)[0]
        D = _hamming_matrix(H[idx], H[tr])
        nn = D.argmin(1); nd = D.min(1)
        same_cls = cls[idx] == cls[tr[nn]]
        res[f"{s}_vs_train"] = {
            "n": int(len(idx)),
            "pct_dist0": round(float((nd == 0).mean()), 4),
            "pct_dist_le4": round(float((nd <= 4).mean()), 4),
            "pct_dist_le8": round(float((nd <= 8).mean()), 4),
            "median_nearest_dist": float(np.median(nd)),
            "nearest_is_same_class_when_le8": round(float(same_cls[nd <= 8].mean()), 4)
            if (nd <= 8).any() else None,
        }
        nearest[s] = (idx, nd)
    # val vs test as well (test also leaks if it mirrors val)
    iv, it = np.where(split == "val")[0], np.where(split == "test")[0]
    res["test_vs_val_pct_dist_le4"] = round(float((_hamming_matrix(H[it], H[iv]).min(1) <= 4).mean()), 4)

    # does accuracy depend on having a near-duplicate in train?
    if test_correct is not None:
        idx, nd = nearest["test"]
        paths = [Path(p).as_posix() for p, _ in test_samples]
        order = {Path(items[i][2]).as_posix(): k for k, i in enumerate(idx)}
        correct = np.array(test_correct)
        # ImageFolder sample order == sorted class then sorted file == our `items` order for test
        near = np.array([nd[order[p]] <= 8 for p in paths])
        res["test_accuracy_if_near_duplicate_in_train_le8"] = {
            "n_near": int(near.sum()),
            "acc_near": round(float(correct[near].mean()), 4) if near.any() else None,
            "n_not_near": int((~near).sum()),
            "acc_not_near": round(float(correct[~near].mean()), 4) if (~near).any() else None}

    # filename-based signals
    pats = Counter(re.sub(r"\d+", "N", i[2].name.lower()) for i in items)
    res["filename_patterns_top"] = pats.most_common(6)
    ts_train = defaultdict(list); ts_held = []
    num_train = defaultdict(list); num_held = []
    for s, c, f in items:
        mt = _TS.search(f.name)
        if mt:
            t = datetime.strptime(mt.group(1) + mt.group(2), "%Y%m%d%H%M%S").timestamp()
            (ts_train[c].append(t) if s == "train" else ts_held.append((c, t)))
        mn = _NUM.match(f.name)
        if mn:
            (num_train[c].append(int(mn.group(1))) if s == "train" else num_held.append((c, int(mn.group(1)))))
    if ts_held:
        gaps = np.array([min((abs(t - u) for u in ts_train[c]), default=1e12) for c, t in ts_held])
        res["timestamped_filenames_heldout_vs_train_same_class"] = {
            "n_heldout": len(gaps), "pct_within_60s": round(float((gaps <= 60).mean()), 4),
            "pct_within_1h": round(float((gaps <= 3600).mean()), 4),
            "pct_same_day": round(float((gaps <= 86400).mean()), 4)}
    if num_held:
        gaps = np.array([min((abs(n - m) for m in num_train[c]), default=10**9) for c, n in num_held])
        res["sequential_filenames_heldout_vs_train_same_class"] = {
            "n_heldout": len(gaps), "pct_adjacent_le1": round(float((gaps <= 1).mean()), 4),
            "pct_within_3": round(float((gaps <= 3).mean()), 4)}
    return res


# ============================================================
# Reporting
# ============================================================
def _pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def write_markdown(rep: dict) -> str:
    L = [f"# Baseline evaluation  ({rep['generated']})", "",
         "Read-only evaluation of the saved model + FAISS index. Nothing was retrained or rebuilt.", ""]
    c = rep.get("classifier")
    if c:
        L += ["## Classifier (MobileNetV3-Small)", "",
              "| split | n | accuracy | macro-F1 |", "|---|---|---|---|"]
        for k, lab in (("val", "val"), ("test", "test"), ("test_background_swapped", "test, backgrounds swapped")):
            m = c[k]; L.append(f"| {lab} | {m['n']} | {_pct(m['accuracy'])} | {_pct(m['macro_f1'])} |")
        L += ["", f"Mean confidence: correct {c['mean_confidence_correct']}, wrong {c['mean_confidence_wrong']}", "",
              f"Classes below 90% held-out accuracy: {len(c['classes_below_90pct_heldout'])} / {c['n_classes']}", "",
              "Top confusions (held-out, true -> predicted):", ""]
        L += [f"- {x['true']} -> {x['predicted']}: {x['count']}" for x in c["top_confusions_heldout"]]
        L += ["", "### Per-class accuracy (worst first; held-out = val + test)", "",
              "| class | train n | held-out n | held-out acc | test acc | test acc, bg swapped |", "|---|---|---|---|---|---|"]
        for r in c["per_class"]:
            L.append(f"| {r['class']} | {r['n_train']} | {r['n_heldout']} | {_pct(r['acc_heldout'])} | "
                     f"{_pct(r['acc_test'])} | {_pct(r['acc_test_bg_swapped'])} |")
        cov = c["rag_coverage_of_classifier_classes"]
        L += ["", f"RAG knowledge-base coverage of classifier classes: **{cov['with_kb_chunks']} / {cov['classes']}**", ""]
    a = rep.get("leakage_audit")
    if a:
        L += ["## Duplicate / leakage audit", "", f"Images scanned: {a['n_images']}", "",
              f"- Exact duplicate groups: {a['exact_duplicate_groups']} "
              f"(across splits: {a['exact_duplicates_across_splits']}, across classes: {a['exact_duplicates_across_classes']})"]
        for s in ("val", "test"):
            v = a[f"{s}_vs_train"]
            L.append(f"- {s} vs train (64-bit dHash): identical {_pct(v['pct_dist0'])}, "
                     f"near (<=4 bits) {_pct(v['pct_dist_le4'])}, similar (<=8 bits) {_pct(v['pct_dist_le8'])}, "
                     f"median nearest distance {v['median_nearest_dist']}")
        L.append(f"- test vs val near (<=4 bits): {_pct(a['test_vs_val_pct_dist_le4'])}")
        if "test_accuracy_if_near_duplicate_in_train_le8" in a:
            v = a["test_accuracy_if_near_duplicate_in_train_le8"]
            L.append(f"- Test accuracy WITH a near-duplicate in train: {_pct(v['acc_near'])} (n={v['n_near']}); "
                     f"WITHOUT: {_pct(v['acc_not_near'])} (n={v['n_not_near']})")
        for k in ("timestamped_filenames_heldout_vs_train_same_class", "sequential_filenames_heldout_vs_train_same_class"):
            if k in a:
                L.append(f"- {k}: {a[k]}")
        L.append(f"- Filename patterns: {a['filename_patterns_top']}")
        L.append("")
    r = rep.get("rag")
    if r:
        L += ["## RAG retrieval", "",
              f"{r['n_questions']} questions, {r['n_chunks']} chunks, {len(r['kb_plants'])} plants in the index. "
              f"Question categories: {r['category_counts']}", "",
              "`plant` = a top-k chunk comes from the expected plant. "
              "`plant+category` = a top-k chunk from the expected plant that contains the expected section "
              "(Medicinal Uses / Preparation / Precautions / Misconceptions).", "",
              "| pipeline | match | Hit@1 | Hit@3 | Hit@5 |", "|---|---|---|---|---|"]
        for name in ("production_retriever", "raw_faiss"):
            for key, lab in (("plant_match", "plant"), ("plant_and_category_match", "plant+category")):
                m = r[name][key]
                L.append(f"| {name} | {lab} | {_pct(m['hit@1'])} | {_pct(m['hit@3'])} | {_pct(m['hit@5'])} |")
        for name in ("production_retriever", "raw_faiss"):
            L += ["", f"### {name}: plant+category by question category", "",
                  "| category | n | Hit@1 | Hit@3 | Hit@5 |", "|---|---|---|---|---|"]
            for cat, m in r[name]["by_category_plant_and_category"].items():
                L.append(f"| {cat} | {m['n']} | {_pct(m['hit@1'])} | {_pct(m['hit@3'])} | {_pct(m['hit@5'])} |")
            L.append(f"\nTop-1 from the wrong plant: {r[name]['top1_wrong_plant']} / {r['n_questions']}")
            misses = r[name]["misses_at_5_plant_and_category"]
            L.append(f"Questions with no plant+category hit in top 5: {len(misses)}")
            L += [f"- [{m['plant']} / {m['category']}] {m['question']}  -> {m['top5']}" for m in misses]
        if "by_set" in r["production_retriever"]:
            L += _md_by_set(r)
    return "\n".join(L) + "\n"


def _md_by_set(r: dict) -> list[str]:
    def row(label, g):
        a = g.get("answer_chunk_match")
        ans = f"{_pct(a['hit@1'])} / {_pct(a['hit@3'])} / {_pct(a['hit@5'])} (n={a['n']})" if a else "-"
        pc, pm = g["plant_and_category_match"], g["plant_match"]
        return (f"| {label} | {g['n']} | {_pct(pm['hit@1'])} | {_pct(pc['hit@1'])} | {_pct(pc['hit@3'])} | "
                f"{_pct(pc['hit@5'])} | {ans} | {g['top1_wrong_plant']} |")

    head = ["| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |",
            "|---|---|---|---|---|---|---|---|"]
    L = ["", "## RAG retrieval by question set", "",
         f"{r['n_original_questions']} original questions + {r['n_pilot_questions']} pilot questions, "
         f"{r['n_chunks']} chunks. 'answer-chunk' = the chunk of the right plant and category that contains the "
         "phrases the answer needs (pilot questions only)."]
    for pipe in ("production_retriever", "raw_faiss"):
        bs = r[pipe]["by_set"]
        L += ["", f"### {pipe}", ""] + head
        for gname in ("original", "pilot", "combined"):
            if gname in bs:
                L.append(row(gname, bs[gname]))
        for gname in ("original", "pilot", "combined"):
            if gname not in bs:
                continue
            L += ["", f"{pipe} / {gname}: by category", ""] + head
            L += [row(c, g) for c, g in bs[gname]["by_category"].items()]
            L += ["", f"{pipe} / {gname}: by plant", ""] + head
            L += [row(p, g) for p, g in bs[gname]["by_plant"].items()]
            if "by_style" in bs[gname]:
                L += ["", f"{pipe} / {gname}: by question style", ""] + head
                L += [row(s_, g) for s_, g in bs[gname]["by_style"].items()]
        for key, lab in (("misses_at_5_plant_and_category", "no plant+category hit in top 5"),
                         ("misses_at_5_answer_chunk", "no answer-chunk hit in top 5")):
            ms = bs["combined"][key]
            L += ["", f"{pipe}: {lab}: {len(ms)}"]
            L += [f"- [{m['plant']} / {m['category']}] {m['question']} -> {m['top5']}" for m in ms]
    return L


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-rag", action="store_true")
    ap.add_argument("--skip-cls", action="store_true")
    ap.add_argument("--skip-leakage", action="store_true")
    ap.add_argument("--out-prefix", default="baseline_report",
                    help="report file name prefix (default: baseline_report)")
    args = ap.parse_args()

    rep: dict = {"generated": datetime.now().isoformat(timespec="seconds")}
    cls = None
    if not args.skip_cls:
        print("[1/3] classifier ...", flush=True)
        cls = evaluate_classifier()
        rep["classifier"] = {k: v for k, v in cls.items() if not k.startswith("_")}
    if not args.skip_leakage:
        print("[2/3] duplicate / leakage audit ...", flush=True)
        rep["leakage_audit"] = audit_leakage(cls and cls["_test_correct"], cls and cls["_test_ds_samples"])
    if not args.skip_rag:
        print("[3/3] RAG retrieval ...", flush=True)
        rep["rag"] = evaluate_rag()

    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / f"{args.out_prefix}.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    md = write_markdown(rep)
    (REPORT_DIR / f"{args.out_prefix}.md").write_text(md, encoding="utf-8")
    print(f"\nWrote {REPORT_DIR / (args.out_prefix + '.md')} and {args.out_prefix}.json")


if __name__ == "__main__":
    main()
