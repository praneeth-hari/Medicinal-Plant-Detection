"""
test_rag.py — Tests for the RAG components (chunking, FAISS store, retriever, generator).
All tests run offline: embeddings are faked and the Ollama HTTP call is mocked.
"""
import asyncio

import httpx
import pytest

from rag.embeddings import EmbeddingService
from rag.generator import ResponseGenerator
from rag.retriever import DocumentRetriever
from rag.vector_store import VectorStoreService


class FakeEmbedder:
    """Deterministic 3-d embeddings: one axis per topic keyword."""

    def embed_text(self, text):
        t = text.lower()
        return [float("tulsi" in t), float("neem" in t), float("ginger" in t) or 0.1]


def _build_store(tmp_path):
    docs = [
        ("tulsi about cough", {"plant": "Tulsi", "source": "tulsi_monograph"}, [1, 0, 0]),
        ("tulsi precautions", {"plant": "Tulsi", "source": "tulsi_monograph"}, [0.9, 0.1, 0]),
        ("tulsi dosage", {"plant": "Tulsi", "source": "tulsi_monograph"}, [0.8, 0.2, 0]),
        ("neem skin uses", {"plant": "Neem", "source": "neem_monograph"}, [0, 1, 0]),
        ("ginger nausea", {"plant": "Ginger", "source": "ginger_monograph"}, [0, 0, 1]),
    ]
    store = VectorStoreService(str(tmp_path), "test")
    store.create_index([d[2] for d in docs], [d[0] for d in docs], [d[1] for d in docs])
    return store


class TestChunking:
    def test_short_text_is_single_chunk(self):
        assert EmbeddingService.chunk_text("Short text.") == ["Short text."]

    def test_empty_text_gives_no_chunks(self):
        assert EmbeddingService.chunk_text("   ") == []

    def test_long_text_is_split_within_size(self):
        text = " ".join(f"Sentence number {i} is here." for i in range(80))
        chunks = EmbeddingService.chunk_text(text, chunk_size=200, overlap=20)
        assert len(chunks) > 1
        assert all(len(c) <= 260 for c in chunks)  # size + overlap slack


class TestVectorStore:
    def test_search_returns_nearest_first(self, tmp_path):
        store = _build_store(tmp_path)
        results = store.search([0, 1, 0], n_results=2)
        assert results[0]["document"] == "neem skin uses"
        assert results[0]["score"] > results[1]["score"]

    def test_index_persists_and_reloads(self, tmp_path):
        _build_store(tmp_path)
        reloaded = VectorStoreService(str(tmp_path), "test")
        assert reloaded.load_index() is True
        assert reloaded.count == 5
        assert reloaded.search([0, 0, 1], n_results=1)[0]["document"] == "ginger nausea"

    def test_empty_store_returns_nothing(self, tmp_path):
        store = VectorStoreService(str(tmp_path), "empty")
        assert store.is_loaded is False
        assert store.search([1, 0, 0]) == []
        assert store.load_index() is False


class TestRetriever:
    def test_empty_knowledge_base_returns_no_documents(self, tmp_path):
        retriever = DocumentRetriever(VectorStoreService(str(tmp_path), "empty"), FakeEmbedder())
        assert retriever.retrieve("tulsi") == []
        assert "No relevant documents" in retriever.format_context([])

    def test_named_plant_is_boosted_and_deduplicated(self, tmp_path):
        retriever = DocumentRetriever(_build_store(tmp_path), FakeEmbedder())
        docs = retriever.retrieve("tell me about tulsi", top_k=4)
        plants = [d["metadata"]["plant"] for d in docs]
        assert plants[0] == "Tulsi"
        assert plants.count("Tulsi") <= 3  # max 2 via suppression, extra only as top-up filler

    def test_boost_names_come_from_the_loaded_chunks(self, tmp_path):
        store = _build_store(tmp_path)
        retriever = DocumentRetriever(store, FakeEmbedder())
        assert retriever._known_plant_names() == ["ginger", "neem", "tulsi"]
        store.add_documents([[1, 1, 1]], ["guava leaf"], [{"plant": "Guava"}])
        assert "guava" in retriever._known_plant_names()  # cache refreshes when the chunk count changes
        empty = DocumentRetriever(VectorStoreService(str(tmp_path), "empty"), FakeEmbedder())
        assert empty._known_plant_names() == []

    def test_current_kb_plants_are_boost_candidates(self, tmp_path):
        from scripts.build_index import PLANT_DOCUMENTS

        metas = [{"plant": p} for p in [d["plant"] for d in PLANT_DOCUMENTS] + ["Guava", "Castor", "Tomato"]]
        store = VectorStoreService(str(tmp_path), "kb")
        store.create_index([[1, 0, 0]] * len(metas), ["x"] * len(metas), metas)
        names = DocumentRetriever(store, FakeEmbedder())._known_plant_names()
        assert len(names) == 23 and {"guava", "castor", "tomato"} <= set(names)

    @pytest.mark.parametrize("query, expected", [
        ("does it appear safe, or belong on a label?", {}),                       # pea / bel inside other words
        ("how do i make lemongrass tea", {"Lemongrass": 0.25, "Lemon": -0.1}),    # lemon is not inside lemongrass
        ("what are neem's uses", {"Neem": 0.25, "Pea": -0.1}),                    # possessive still matches
    ])
    def test_plant_names_match_whole_words_only(self, tmp_path, query, expected):
        plants = ["Pea", "Lemon", "Lemongrass", "Neem", "Bael"]
        store = VectorStoreService(str(tmp_path), "words")
        store.create_index([[0.2, 0.2 + i / 10, 0.5] for i in range(len(plants))], plants,
                           [{"plant": p, "source": p.lower()} for p in plants])
        retriever = DocumentRetriever(store, FakeEmbedder())
        raw = {d["id"]: d["score"] for d in store.search(FakeEmbedder().embed_text(query), n_results=10)}
        deltas = {d["metadata"]["plant"]: round(d["score"] - raw[d["id"]], 2) for d in retriever.retrieve(query, top_k=5)}
        if not expected:
            assert set(deltas.values()) == {0.0}
        else:
            assert {p: deltas[p] for p in expected} == expected
            assert all(v == -0.1 for p, v in deltas.items() if p not in expected)

    def test_context_and_source_references(self, tmp_path):
        retriever = DocumentRetriever(_build_store(tmp_path), FakeEmbedder())
        docs = retriever.retrieve("neem", top_k=2)
        context = retriever.format_context(docs)
        assert context.startswith("[Source 1]")
        refs = retriever.to_source_references(docs)
        assert refs[0]["document"] == "neem_monograph"
        assert set(refs[0]) == {"document", "page", "relevance_score", "snippet"}


class TestGenerator:
    def test_prompt_contains_context_history_and_query(self):
        gen = ResponseGenerator()
        messages = gen.format_prompt(
            "What is tulsi?", "CONTEXT-TEXT",
            chat_history=[{"role": "user", "content": "earlier"}],
        )
        assert messages[0]["role"] == "system"
        assert "CONTEXT-TEXT" in messages[1]["content"]
        assert messages[-2] == {"role": "user", "content": "earlier"}
        assert messages[-1] == {"role": "user", "content": "What is tulsi?"}

    def test_generate_sends_options_and_returns_answer(self, monkeypatch):
        seen = {}

        async def fake_post(self, url, json=None, **kwargs):
            seen["url"], seen["json"] = url, json
            return httpx.Response(
                200, json={"message": {"content": "  Grounded answer [Source 1]  "}},
                request=httpx.Request("POST", url),
            )

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
        gen = ResponseGenerator(model_name="m", base_url="http://ollama.test")
        answer = asyncio.run(gen.generate("q", "ctx", max_tokens=99, temperature=0.0))
        assert answer == "Grounded answer [Source 1]"
        assert seen["url"] == "http://ollama.test/api/chat"
        assert seen["json"]["model"] == "m"
        assert seen["json"]["options"] == {"temperature": 0.0, "num_predict": 99}
        assert seen["json"]["stream"] is False

    def test_generate_falls_back_when_ollama_is_down(self, monkeypatch):
        async def boom(self, url, **kwargs):
            raise httpx.ConnectError("refused")

        monkeypatch.setattr(httpx.AsyncClient, "post", boom)
        answer = asyncio.run(ResponseGenerator(model_name="qwen2.5:3b").generate("q", "ctx"))
        assert "ollama pull qwen2.5:3b" in answer

    def test_empty_model_reply_is_handled(self, monkeypatch):
        async def empty(self, url, **kwargs):
            return httpx.Response(200, json={"message": {"content": ""}}, request=httpx.Request("POST", url))

        monkeypatch.setattr(httpx.AsyncClient, "post", empty)
        assert "unable to generate" in asyncio.run(ResponseGenerator().generate("q", "ctx"))
