"""
conftest.py — Shared pytest setup
=================================
Points the app at a throw-away SQLite database / upload folder *before* any
application module is imported, so tests never touch the real data, and
isolates the chat audit log and metrics files.
"""
import os
import sys
import tempfile

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "backend"))
sys.path.insert(0, _ROOT)

_TMP = tempfile.mkdtemp(prefix="mediplant_tests_")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TMP}/test.db".replace("\\", "/")
os.environ["UPLOAD_DIR"] = f"{_TMP}/uploads".replace("\\", "/")
os.environ["DEBUG"] = "false"
os.environ["LOG_LEVEL"] = "WARNING"


class StubPipeline:
    """Stand-in for the RAG pipeline: no embedding model, no Ollama."""

    def __init__(self):
        self.calls = []

    async def _reply(self, query, **kwargs):
        self.calls.append({"query": query, **kwargs})
        return {
            "answer": f"Stub answer about: {query}",
            "sources": [{
                "document": "tulsi_monograph",
                "page": 0,
                "relevance_score": 0.9,
                "snippet": "Tulsi snippet",
            }],
        }

    async def answer(self, query, **kwargs):
        return await self._reply(query, **kwargs)

    async def answer_with_history(self, query, chat_history, **kwargs):
        return await self._reply(query, history=len(chat_history), **kwargs)


@pytest.fixture(autouse=True)
def isolate_side_files(tmp_path, monkeypatch):
    """Redirect the audit log and metrics files to a per-test temp dir."""
    from services import chat_service, metrics

    monkeypatch.setattr(chat_service, "AUDIT_PATH", str(tmp_path / "audit.json"))
    monkeypatch.setattr(metrics, "METRICS_FILE", str(tmp_path / "metrics.json"))
    monkeypatch.setattr(metrics, "_DATA_DIR", str(tmp_path))

    from api.v1.endpoints import control_tower

    monkeypatch.setattr(control_tower, "SETTINGS_FILE", str(tmp_path / "ct_settings.json"))
    monkeypatch.setattr(control_tower, "AUDIT_LOG_FILE", str(tmp_path / "ct_audit.json"))


@pytest.fixture
def stub_pipeline(monkeypatch):
    """Make ChatService use a stub pipeline instead of the real RAG stack."""
    import rag.pipeline

    stub = StubPipeline()
    monkeypatch.setattr(rag.pipeline, "get_rag_pipeline", lambda: stub)
    return stub


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient (runs lifespan: creates tables + local user)."""
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as c:
        yield c
