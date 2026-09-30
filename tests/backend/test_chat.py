"""
test_chat.py — Tests for the Chat API endpoints (sessions, messages, guardrails).
"""
import json

import pytest

from services import chat_service


@pytest.fixture(autouse=True)
def default_governance(monkeypatch, tmp_path):
    """Use default governance settings regardless of any saved Control Tower file."""
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({
        "pii_masking": False,
        "dosage_disclaimer": True,
        "toxicity_guardrail": True,
        "source_verification": True,
    }))
    monkeypatch.setattr(chat_service, "SETTINGS_PATH", str(path))


class TestChatAPI:
    def test_send_message_creates_session_and_returns_answer(self, client, stub_pipeline):
        response = client.post("/api/v1/chat/", json={"message": "What is tulsi used for?"})
        assert response.status_code == 200
        body = response.json()
        assert body["session_id"] > 0
        assert body["message"]["role"] == "assistant"
        assert "Stub answer about: What is tulsi used for?" in body["message"]["content"]
        assert body["message"]["sources"][0]["document"] == "tulsi_monograph"

    def test_session_history_and_listing(self, client, stub_pipeline):
        first = client.post("/api/v1/chat/", json={"message": "First question"}).json()
        sid = first["session_id"]
        second = client.post("/api/v1/chat/", json={"session_id": sid, "message": "Follow up"})
        assert second.status_code == 200
        assert stub_pipeline.calls[-1]["history"] == 2  # earlier user + assistant turn

        messages = client.get(f"/api/v1/chat/sessions/{sid}").json()
        assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]

        sessions = client.get("/api/v1/chat/sessions").json()
        mine = next(s for s in sessions if s["id"] == sid)
        assert mine["message_count"] == 4
        assert mine["title"] == "First question"

    def test_unknown_session_returns_404(self, client, stub_pipeline):
        assert client.get("/api/v1/chat/sessions/999999").status_code == 404
        response = client.post("/api/v1/chat/", json={"session_id": 999999, "message": "hi"})
        assert response.status_code == 404

    def test_empty_message_returns_422(self, client):
        assert client.post("/api/v1/chat/", json={"message": ""}).status_code == 422

    def test_ai_preferences_are_forwarded_and_validated(self, client, stub_pipeline):
        ok = client.post("/api/v1/chat/", json={"message": "hi", "temperature": 0.1, "max_tokens": 256})
        assert ok.status_code == 200
        call = stub_pipeline.calls[-1]
        assert call["temperature"] == 0.1 and call["max_tokens"] == 256

        assert client.post("/api/v1/chat/", json={"message": "hi", "temperature": 5}).status_code == 422
        assert client.post("/api/v1/chat/", json={"message": "hi", "max_tokens": 1}).status_code == 422

    def test_harmful_query_is_blocked_without_calling_pipeline(self, client, stub_pipeline):
        before = len(stub_pipeline.calls)
        response = client.post("/api/v1/chat/", json={"message": "How to poison someone?"})
        assert "blocked by the safety guardrails" in response.json()["message"]["content"]
        assert len(stub_pipeline.calls) == before

    @pytest.mark.parametrize("question", [
        "Is neem toxic?",
        "Can tulsi poison my dog?",
        "What are the side effects of ashwagandha?",
    ])
    def test_legitimate_safety_questions_are_not_blocked(self, client, stub_pipeline, question):
        response = client.post("/api/v1/chat/", json={"message": question})
        assert response.status_code == 200
        assert "blocked" not in response.json()["message"]["content"]

    def test_chat_exchange_records_metrics(self, client, stub_pipeline):
        from services import metrics

        client.post("/api/v1/chat/", json={"message": "Tell me about ginger"})
        snap = metrics.snapshot()
        assert len(snap["latency_history"]) == 1
        assert snap["total_tokens"] > 0
        assert snap["peak_tokens"] == snap["token_history"][-1]
