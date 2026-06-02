"""
API v1 — Aggregate Router
==========================

Collects all v1 endpoint sub-routers into a single ``APIRouter``
that can be mounted on the main FastAPI application with a version
prefix (e.g., ``/api/v1``).
"""
from __future__ import annotations

from fastapi import APIRouter

from api.v1.endpoints import auth, chat, detection, plants, health

api_v1_router = APIRouter()

# Health check (no prefix — available at /api/v1/health)
api_v1_router.include_router(
    health.router,
    tags=["Health"],
)

# Feature endpoints
api_v1_router.include_router(
    plants.router,
    prefix="/plants",
    tags=["Plants"],
)
api_v1_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)
api_v1_router.include_router(
    detection.router,
    prefix="/detect",
    tags=["Detection"],
)
api_v1_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)
