"""
System Info endpoint — returns live configuration values for the About page.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from config.settings import settings

router = APIRouter()


class SystemInfo(BaseModel):
    backend_framework: str
    app_version: str
    database: str
    rag_llm_model: str
    embedding_model: str
    classification_model: str


@router.get("", response_model=SystemInfo)
async def get_system_info() -> SystemInfo:
    db_type = "SQLite" if settings.is_sqlite else "PostgreSQL"
    return SystemInfo(
        backend_framework="FastAPI",
        app_version=settings.APP_VERSION,
        database=f"{db_type} + FAISS",
        rag_llm_model=f"Ollama / {settings.OLLAMA_MODEL}",
        embedding_model=settings.EMBEDDING_MODEL,
        classification_model="MobileNetV3-Small" if Path(settings.MODEL_PATH).exists() else "MobileNetV3-Small (weights missing)",
    )
