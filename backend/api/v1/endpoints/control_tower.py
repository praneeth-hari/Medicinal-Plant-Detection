"""
Control Tower Endpoints
=======================
API endpoints for managing governance settings, viewing telemetry stats,
and checking audit logs.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from typing import List

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from config.database import get_db
from config.settings import settings as app_settings
from schemas.control_tower import ControlTowerSettings, ControlTowerStats, AuditLogEntry, ServiceHealth
from services import metrics
from schemas.user import TokenData
from models.chat import ChatMessage, ChatSession, MessageRole

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

router = APIRouter()

# 3 levels up: endpoints/ → v1/ → api/ → backend/, then into data/
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
SETTINGS_FILE = os.path.join(DATA_DIR, "control_tower_settings.json")
AUDIT_LOG_FILE = os.path.join(DATA_DIR, "control_tower_audit_logs.json")

def _load_settings_sync() -> ControlTowerSettings:
    """Synchronous settings loader — run via asyncio.to_thread."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return ControlTowerSettings(**data)
        except Exception:
            pass
    return ControlTowerSettings()

def _save_settings_sync(settings: ControlTowerSettings) -> None:
    """Synchronous settings writer — run via asyncio.to_thread."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings.model_dump(), f, indent=2)

def _load_audit_logs_sync() -> List[dict]:
    """Synchronous audit log reader — run via asyncio.to_thread."""
    if os.path.exists(AUDIT_LOG_FILE):
        try:
            with open(AUDIT_LOG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

@router.get("/settings", response_model=ControlTowerSettings)
async def get_settings(current_user: TokenData = Depends(get_current_user)):
    """Retrieve the active governance settings."""
    return await asyncio.to_thread(_load_settings_sync)

@router.post("/settings", response_model=ControlTowerSettings)
async def update_settings(
    settings_in: ControlTowerSettings,
    current_user: TokenData = Depends(get_current_user)
):
    """Update active governance settings."""
    await asyncio.to_thread(_save_settings_sync, settings_in)
    return settings_in

@router.get("/audit", response_model=List[AuditLogEntry])
async def get_audit_logs(current_user: TokenData = Depends(get_current_user)):
    """Retrieve recent query compliance audit log entries."""
    logs = await asyncio.to_thread(_load_audit_logs_sync)
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

async def _probe_ollama() -> ServiceHealth:
    """Check the local Ollama server and that the configured model is installed."""
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{app_settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags")
        ms = (time.perf_counter() - start) * 1000
        if resp.status_code != 200:
            return ServiceHealth(name="Ollama LLM", healthy=False, latency_ms=round(ms, 1), detail=f"HTTP {resp.status_code}")
        names = [m.get("name", "") for m in resp.json().get("models", [])]
        has_model = any(n == app_settings.OLLAMA_MODEL or n.startswith(app_settings.OLLAMA_MODEL + ":") for n in names)
        return ServiceHealth(
            name="Ollama LLM", healthy=has_model, latency_ms=round(ms, 1),
            detail=None if has_model else f"Model '{app_settings.OLLAMA_MODEL}' not installed",
        )
    except Exception as e:
        return ServiceHealth(name="Ollama LLM", healthy=False, detail=str(e)[:120] or "Unreachable")


@router.get("/stats", response_model=ControlTowerStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Retrieve system performance metrics combined with database totals."""
    # Database health + totals (timed SELECT 1 doubles as the DB latency probe)
    db_start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        db_health = ServiceHealth(name="SQLite Database", healthy=True, latency_ms=round((time.perf_counter() - db_start) * 1000, 1))
    except Exception as e:
        db_health = ServiceHealth(name="SQLite Database", healthy=False, detail=str(e)[:120])

    sessions_query = await db.execute(select(func.count()).select_from(ChatSession))
    active_sessions = sessions_query.scalar() or 0

    queries_query = await db.execute(select(func.count()).select_from(ChatMessage).where(ChatMessage.role == MessageRole.USER))
    total_queries = queries_query.scalar() or 0

    # Real system telemetry via psutil (falls back to safe defaults if unavailable)
    if _PSUTIL_AVAILABLE:
        cpu = round(psutil.cpu_percent(interval=0.1), 1)
        ram = round(psutil.virtual_memory().percent, 1)
    else:
        cpu = 0.0
        ram = 0.0

    # FAISS knowledge index
    try:
        from rag.vector_store import get_vector_store
        store = get_vector_store()
        faiss_health = ServiceHealth(
            name="FAISS Vector Index", healthy=store.is_loaded,
            detail=f"{store.count} chunks indexed" if store.is_loaded else "Index not built",
        )
    except Exception as e:
        faiss_health = ServiceHealth(name="FAISS Vector Index", healthy=False, detail=str(e)[:120])

    ollama_health = await _probe_ollama()
    m = await asyncio.to_thread(metrics.snapshot, 10)

    return ControlTowerStats(
        cpu_usage=cpu,
        memory_usage=ram,
        active_sessions=active_sessions,
        db_health="Healthy" if db_health.healthy else "Unhealthy",
        ollama_availability="Available" if ollama_health.healthy else "Unavailable",
        total_queries=total_queries,
        avg_latency_ms=m["avg_latency_ms"],
        latency_history=m["latency_history"],
        token_history=m["token_history"],
        total_tokens=m["total_tokens"],
        peak_tokens=m["peak_tokens"],
        services=[db_health, ollama_health, faiss_health],
        timestamp=datetime.now(timezone.utc),
    )
