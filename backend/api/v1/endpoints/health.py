"""
Health & Status Endpoints (v1)
===============================
Detailed health checks scoped to the ``/api/v1`` prefix.
Includes database connectivity verification.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    summary="API v1 health check",
    description="Returns detailed health status including database connectivity.",
)
async def api_health_check(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Detailed health check with database connectivity verification.

    Checks:
    - Database connectivity (SELECT 1)

    Returns a JSON payload with overall status and per-check results.
    """
    health: dict = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_version": "v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {},
    }

    # ── Database connectivity check ──────────────────────────────
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health["checks"]["database"] = {
            "status": "connected",
            "type": "sqlite" if settings.is_sqlite else "other",
        }
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        health["status"] = "degraded"
        health["checks"]["database"] = {
            "status": "disconnected",
            "error": str(e),
        }

    return health
