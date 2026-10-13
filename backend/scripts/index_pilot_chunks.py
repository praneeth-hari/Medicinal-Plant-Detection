"""
Add the approved pilot chunks to the production FAISS index
===========================================================

Run AFTER ``python -m scripts.build_index`` (which builds the original 40 chunks).
Uses the existing embedding service and VectorStoreService.add_documents; it adds no new
retrieval method.

Pre-flight checks (any failure aborts before the index is touched):
  * every pilot plant passes scripts.kb_render (confirmed identity, validator, source ids)
  * data/knowledge_base/pilot/pilot_chunks.json equals what the renderer produces now
  * every chunk's class_label resolves to exactly one plants row (matching scientific name)
  * no chunk id is already in the index

    cd backend
    python -m scripts.index_pilot_chunks --check    # pre-flight only
    python -m scripts.index_pilot_chunks            # pre-flight + add to the index
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND))

from scripts import kb_render  # noqa: E402

DB_PATH = _BACKEND / "medicinal_plants.db"
PERSIST_DIR = "./data/embeddings"  # same relative path build_index.py uses (run from backend/)


def preflight(pilot_dir: Path, db_path: Path) -> tuple[dict, list[str]]:
    """Return (pilot_chunks_json, problems)."""
    problems: list[str] = []
    sources = json.loads(kb_render.SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
    coverage = kb_render.load_coverage()

    rendered = []
    for path in sorted(p for p in pilot_dir.glob("*.json") if p.name != "pilot_chunks.json"):
        chunks, errors, _ = kb_render.process_plant(path, sources, coverage)
        problems += [f"{path.name}: {e}" for e in errors]
        rendered += chunks

    committed = json.loads((pilot_dir / "pilot_chunks.json").read_text(encoding="utf-8"))
    if (committed["ids"] != [c["id"] for c in rendered]
            or committed["documents"] != [c["document"] for c in rendered]
            or committed["metadatas"] != [c["metadata"] for c in rendered]):
        problems.append("pilot_chunks.json is out of date with the plant files (re-run scripts.kb_render)")

    conn = sqlite3.connect(db_path)
    try:
        for label in sorted({m["class_label"] for m in committed["metadatas"]}):
            row = coverage.get(label)
            if row is None or row["identity_status"] != "confirmed":
                problems.append(f"class_label '{label}' is not a confirmed identity")
            rows = conn.execute("SELECT id, scientific_name FROM plants WHERE class_label=?", (label,)).fetchall()
            sci = {m["scientific_name"] for m in committed["metadatas"] if m["class_label"] == label}
            if len(rows) != 1:
                problems.append(f"class_label '{label}' resolves to {len(rows)} plants rows (expected 1)")
            elif {rows[0][1]} != sci:
                problems.append(f"class_label '{label}' row has scientific_name '{rows[0][1]}', chunks say {sci}")
    finally:
        conn.close()
    return committed, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="pre-flight only; do not touch the index")
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--dir", default=str(kb_render.PILOT_DIR))
    args = ap.parse_args()

    data, problems = preflight(Path(args.dir), Path(args.db))
    labels = sorted({m["class_label"] for m in data["metadatas"]})
    print(f"Pilot chunks: {len(data['ids'])} across class labels {labels}")
    if problems:
        for p in problems:
            print(f"  PROBLEM {p}")
        return 1
    print("Pre-flight OK (renderer/validator, sources, identities, class_label -> plants rows)")
    if args.check:
        return 0

    from rag.embeddings import get_embedding_service
    from rag.vector_store import VectorStoreService

    store = VectorStoreService(persist_directory=PERSIST_DIR, collection_name="medicinal_plants")
    if not store.load_index():
        print("  PROBLEM no existing index; run scripts.build_index first")
        return 1
    clash = set(data["ids"]) & set(store._ids)
    if clash:
        print(f"  PROBLEM {len(clash)} chunk ids already in the index (not adding twice): {sorted(clash)[:3]}")
        return 1
    before = store.count
    emb = get_embedding_service()
    t0 = time.time()
    vectors = emb.embed_documents(data["documents"])
    store.add_documents(vectors, data["documents"], data["metadatas"], data["ids"])
    print(f"Added {len(data['ids'])} chunks in {time.time() - t0:.1f}s: index {before} -> {store.count} chunks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
