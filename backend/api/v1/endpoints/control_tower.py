"""
Control Tower Endpoints
=======================
API endpoints for managing governance settings, viewing telemetry stats,
and checking audit logs.
"""
from __future__ import annotations

import json
import os
import random
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, require_developer
from schemas.control_tower import ControlTowerSettings, ControlTowerStats, AuditLogEntry
from schemas.user import TokenData
from models.chat import ChatMessage, ChatSession

router = APIRouter()

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
SETTINGS_FILE = os.path.join(DATA_DIR, "control_tower_settings.json")
AUDIT_LOG_FILE = os.path.join(DATA_DIR, "control_tower_audit_logs.json")

def load_settings() -> ControlTowerSettings:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return ControlTowerSettings(**data)
        except Exception:
            pass
    return ControlTowerSettings()

def save_settings(settings: ControlTowerSettings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings.model_dump(), f, indent=2)

def load_audit_logs() -> List[dict]:
    if os.path.exists(AUDIT_LOG_FILE):
        try:
            with open(AUDIT_LOG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

@router.get("/settings", response_model=ControlTowerSettings)
async def get_settings(current_user: TokenData = Depends(require_developer)):
    """Retrieve the active governance settings."""
    return load_settings()

@router.post("/settings", response_model=ControlTowerSettings)
async def update_settings(
    settings_in: ControlTowerSettings,
    current_user: TokenData = Depends(require_developer)
):
    """Update active governance settings."""
    save_settings(settings_in)
    return settings_in

@router.get("/audit", response_model=List[AuditLogEntry])
async def get_audit_logs(current_user: TokenData = Depends(require_developer)):
    """Retrieve recent query compliance audit log entries."""
    logs = load_audit_logs()
    result = []
    for log in logs:
        try:
            log_copy = dict(log)
            if isinstance(log_copy.get("timestamp"), str):
                log_copy["timestamp"] = datetime.fromisoformat(log_copy["timestamp"].replace("Z", "+00:00"))
            result.append(AuditLogEntry(**log_copy))
        except Exception:
            pass
    return result

@router.get("/stats", response_model=ControlTowerStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_developer)
):
    """Retrieve system performance metrics combined with database totals."""
    # Query database for session/message count
    sessions_query = await db.execute(select(func.count()).select_from(ChatSession))
    active_sessions = sessions_query.scalar() or 0

    queries_query = await db.execute(select(func.count()).select_from(ChatMessage))
    total_queries = queries_query.scalar() or 0

    # Mock dynamic telemetry
    cpu = round(random.uniform(12.5, 48.2), 1)
    ram = round(random.uniform(35.1, 62.8), 1)

    latency_history = [random.randint(180, 550) for _ in range(10)]
    token_history = [random.randint(90, 420) for _ in range(10)]
    avg_latency = round(sum(latency_history) / len(latency_history), 1)

    return ControlTowerStats(
        cpu_usage=cpu,
        memory_usage=ram,
        active_sessions=active_sessions,
        db_health="Healthy",
        ollama_availability="Available",
        total_queries=total_queries,
        avg_latency_ms=avg_latency,
        latency_history=latency_history,
        token_history=token_history,
        timestamp=datetime.now(timezone.utc)
    )
