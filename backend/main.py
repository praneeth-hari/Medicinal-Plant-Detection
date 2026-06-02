"""
Medicinal Plant Detection & RAG Assistant — Application Entry Point
===================================================================

FastAPI application factory and bootstrap configuration.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import engine, Base


# ------------------------------------------------------------------
# Lifespan: startup / shutdown hooks
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events.

    Startup:
        - Initialize database tables (dev-only; use Alembic in production).
        - Load ML models into memory (future).
        - Warm up vector-store connection (future).

    Shutdown:
        - Dispose of the database engine connection pool.
        - Release ML model resources (future).
    """
    # ---- Startup ----
    async with engine.begin() as conn:
        # Create tables for development convenience.
        # In production, rely on Alembic migrations instead.
        await conn.run_sync(Base.metadata.create_all)

    yield  # Application is running

    # ---- Shutdown ----
    await engine.dispose()


# ------------------------------------------------------------------
# Application factory
# ------------------------------------------------------------------
app = FastAPI(
    title="Medicinal Plant Detection & RAG Assistant",
    description=(
        "Backend API for identifying medicinal plants from images and "
        "answering natural-language questions about their properties, "
        "uses, and habitat via a Retrieval-Augmented Generation pipeline."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ------------------------------------------------------------------
# CORS Middleware
# ------------------------------------------------------------------
# TODO: Replace wildcard origins with actual frontend URL(s) before deployment.
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",   # React / Next.js dev server
    "http://localhost:5173",   # Vite dev server
    "http://localhost:8080",   # Alternative dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Router registration
# ------------------------------------------------------------------
# Uncomment and import routers as they are implemented:
#
# from api.v1.router import api_v1_router
# app.include_router(api_v1_router, prefix="/api/v1")


# ------------------------------------------------------------------
# Root health-check
# ------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Root health-check endpoint.

    Returns a simple JSON payload confirming the service is running.
    """
    return {
        "status": "healthy",
        "service": "Medicinal Plant Detection & RAG Assistant",
        "version": "0.1.0",
    }
