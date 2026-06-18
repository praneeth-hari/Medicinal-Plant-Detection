"""
test_control_tower.py — Real tests for the AI Control Tower
============================================================
Covers governance settings, stats telemetry, audit logs, and
policy application in the chat service.
"""

import os
import sys
import pytest
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

# Ensure project root and backend are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from api.deps import get_current_user
from schemas.control_tower import ControlTowerSettings
from services.chat_service import ChatService
from models.chat import ChatMessage, ChatSession, MessageRole
from schemas.user import TokenData

# Override get_current_user dependency for testing endpoints
def override_get_current_user():
    return TokenData(user_id=1, username="test_operator")

app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient with lifespan context (creates DB tables)."""
    with TestClient(app) as c:
        yield c


def test_control_tower_settings_defaults():
    """Verify that ControlTowerSettings defaults are set correctly."""
    settings = ControlTowerSettings()
    assert settings.pii_masking is False
    assert settings.dosage_disclaimer is True
    assert settings.toxicity_guardrail is True
    assert settings.source_verification is True


def test_control_tower_endpoints(client):
    """Test control tower API settings and stats retrieval."""
    # Test GET settings
    response = client.get("/api/v1/control-tower/settings")
    assert response.status_code == 200
    settings_data = response.json()
    assert "pii_masking" in settings_data
    assert "dosage_disclaimer" in settings_data

    # Test POST settings
    new_settings = {
        "pii_masking": True,
        "dosage_disclaimer": False,
        "toxicity_guardrail": True,
        "source_verification": False
    }
    post_response = client.post("/api/v1/control-tower/settings", json=new_settings)
    assert post_response.status_code == 200
    assert post_response.json()["pii_masking"] is True
    assert post_response.json()["dosage_disclaimer"] is False

    # Restore defaults
    client.post("/api/v1/control-tower/settings", json={
        "pii_masking": False,
        "dosage_disclaimer": True,
        "toxicity_guardrail": True,
        "source_verification": True
    })

    # Test GET stats
    stats_response = client.get("/api/v1/control-tower/stats")
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    assert "cpu_usage" in stats_data
    assert "memory_usage" in stats_data
    assert "active_sessions" in stats_data
    assert stats_data["db_health"] == "Healthy"


@pytest.mark.asyncio
async def test_chat_service_pii_masking():
    """Verify ChatService masks email, phone, and patient ID when PII masking is enabled."""
    settings_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "data"))
    os.makedirs(settings_dir, exist_ok=True)
    settings_path = os.path.join(settings_dir, "control_tower_settings.json")
    
    # Save test settings
    original_settings = None
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                original_settings = json.load(f)
        except Exception:
            pass

    try:
        with open(settings_path, "w") as f:
            json.dump({
                "pii_masking": True,
                "dosage_disclaimer": False,
                "toxicity_guardrail": False,
                "source_verification": False
            }, f)

        mock_repo = MagicMock()
        mock_repo.get = AsyncMock(return_value=ChatSession(id=1, user_id=1))
        mock_repo.update = AsyncMock()
        mock_repo.get_messages_by_session = AsyncMock(return_value=[])
        
        user_message_record = ChatMessage(
            id=10, session_id=1, role=MessageRole.USER,
            content="Query with test@gmail.com and 123-456-7890 and PT-1002",
            created_at=datetime.now(timezone.utc)
        )
        assistant_message_record = ChatMessage(
            id=11, session_id=1, role=MessageRole.ASSISTANT,
            content="Got it",
            created_at=datetime.now(timezone.utc)
        )
        
        mock_repo.create_message = AsyncMock(side_effect=[user_message_record, assistant_message_record])
        mock_repo.count_messages = AsyncMock(return_value=2)
        
        service = ChatService(repository=mock_repo)
        
        # Mock RAG pipeline answer
        mock_pipeline = MagicMock()
        mock_pipeline.answer = AsyncMock(return_value={"answer": "Got it", "sources": []})
        service._rag_pipeline = mock_pipeline
        
        await service.send_message(session_id=1, user_message="Query with test@gmail.com and 123-456-7890 and PT-1002", user_id=1)
        
        # Verify that the pipeline was called with masked query
        mock_pipeline.answer.assert_called_once()
        called_args = mock_pipeline.answer.call_args[0][0]
        assert "[EMAIL]" in called_args
        assert "[PHONE]" in called_args
        assert "[PATIENT_ID]" in called_args

    finally:
        # Restore settings
        if original_settings:
            with open(settings_path, "w") as f:
                json.dump(original_settings, f)
        elif os.path.exists(settings_path):
            os.remove(settings_path)


@pytest.mark.asyncio
async def test_chat_service_toxicity_guardrail():
    """Verify ChatService blocks queries containing toxic keywords."""
    settings_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "data"))
    os.makedirs(settings_dir, exist_ok=True)
    settings_path = os.path.join(settings_dir, "control_tower_settings.json")
    
    # Save test settings
    original_settings = None
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                original_settings = json.load(f)
        except Exception:
            pass

    try:
        with open(settings_path, "w") as f:
            json.dump({
                "pii_masking": False,
                "dosage_disclaimer": False,
                "toxicity_guardrail": True,
                "source_verification": False
            }, f)

        mock_repo = MagicMock()
        mock_repo.get = AsyncMock(return_value=ChatSession(id=1, user_id=1))
        mock_repo.update = AsyncMock()
        mock_repo.get_messages_by_session = AsyncMock(return_value=[])
        
        user_message_record = ChatMessage(
            id=20, session_id=1, role=MessageRole.USER,
            content="How to poison someone?",
            created_at=datetime.now(timezone.utc)
        )
        assistant_message_record = ChatMessage(
            id=21, session_id=1, role=MessageRole.ASSISTANT,
            content="Your query was blocked by the safety guardrails due to toxicity concerns.",
            created_at=datetime.now(timezone.utc)
        )
        
        mock_repo.create_message = AsyncMock(side_effect=[user_message_record, assistant_message_record])
        mock_repo.count_messages = AsyncMock(return_value=2)
        
        service = ChatService(repository=mock_repo)
        
        # Mock RAG pipeline answer (should not be called!)
        mock_pipeline = MagicMock()
        mock_pipeline.answer = AsyncMock()
        service._rag_pipeline = mock_pipeline
        
        response = await service.send_message(session_id=1, user_message="How to poison someone?", user_id=1)
        
        mock_pipeline.answer.assert_not_called()
        assert "blocked by the safety guardrails" in response.message.content

    finally:
        # Restore settings
        if original_settings:
            with open(settings_path, "w") as f:
                json.dump(original_settings, f)
        elif os.path.exists(settings_path):
            os.remove(settings_path)


@pytest.mark.asyncio
async def test_chat_service_dosage_disclaimer():
    """Verify ChatService appends dosage warning disclaimer to response."""
    settings_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "data"))
    os.makedirs(settings_dir, exist_ok=True)
    settings_path = os.path.join(settings_dir, "control_tower_settings.json")
    
    original_settings = None
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                original_settings = json.load(f)
        except Exception:
            pass

    try:
        with open(settings_path, "w") as f:
            json.dump({
                "pii_masking": False,
                "dosage_disclaimer": True,
                "toxicity_guardrail": False,
                "source_verification": False
            }, f)

        mock_repo = MagicMock()
        mock_repo.get = AsyncMock(return_value=ChatSession(id=1, user_id=1))
        mock_repo.update = AsyncMock()
        mock_repo.get_messages_by_session = AsyncMock(return_value=[])
        
        user_message_record = ChatMessage(
            id=30, session_id=1, role=MessageRole.USER,
            content="What is the dosage for tea?",
            created_at=datetime.now(timezone.utc)
        )
        assistant_message_record = ChatMessage(
            id=31, session_id=1, role=MessageRole.ASSISTANT,
            content="Drink 1 cup. [Disclaimer appended]",
            created_at=datetime.now(timezone.utc)
        )
        
        mock_repo.create_message = AsyncMock(side_effect=[user_message_record, assistant_message_record])
        mock_repo.count_messages = AsyncMock(return_value=2)
        
        service = ChatService(repository=mock_repo)
        
        mock_pipeline = MagicMock()
        mock_pipeline.answer = AsyncMock(return_value={"answer": "Drink 1 cup.", "sources": []})
        service._rag_pipeline = mock_pipeline
        
        await service.send_message(session_id=1, user_message="What is the dosage for tea?", user_id=1)
        
        # Verify that the assistant message created has the disclaimer appended
        created_assistant_data = mock_repo.create_message.call_args_list[1][0][0]
        assert "Disclaimer" in created_assistant_data["content"]
        assert "dosage recommendations" in created_assistant_data["content"]

    finally:
        # Restore settings
        if original_settings:
            with open(settings_path, "w") as f:
                json.dump(original_settings, f)
        elif os.path.exists(settings_path):
            os.remove(settings_path)
