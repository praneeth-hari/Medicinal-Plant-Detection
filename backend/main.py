"""
Medicinal Plant Detection & RAG Assistant — Application Entry Point
===================================================================

FastAPI application factory and bootstrap configuration.

Run with::

    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.logging import setup_logging
from config.database import init_db, close_db
from api.exceptions import register_exception_handlers
from api.v1.router import api_v1_router

# Set up logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Lifespan: startup / shutdown hooks
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events.

    Startup:
        - Log configuration summary
        - Create upload directory
        - Initialize database tables

    Shutdown:
        - Dispose of the database engine connection pool
    """
    # ---- Startup ----
    logger.info("=" * 60)
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("=" * 60)
    logger.info("Debug mode: %s", settings.DEBUG)
    logger.info("Database: %s", settings.DATABASE_URL)
    logger.info("API prefix: %s", settings.API_V1_PREFIX)

    # Create upload directory
    settings.upload_path  # triggers mkdir via property
    logger.info("Upload directory: %s", settings.UPLOAD_DIR)

    # Initialize database tables
    await init_db()
    logger.info("Application startup complete ✓")

    yield  # ── Application is running ──

    # ---- Shutdown ----
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete ✓")


# ------------------------------------------------------------------
# Application factory
# ------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for identifying medicinal plants from images and "
        "answering natural-language questions about their properties, "
        "uses, and habitat via a Retrieval-Augmented Generation pipeline."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ------------------------------------------------------------------
# Global exception handlers
# ------------------------------------------------------------------
register_exception_handlers(app)

# ------------------------------------------------------------------
# CORS Middleware
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Router registration
# ------------------------------------------------------------------
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

logger.info("Routers mounted at %s", settings.API_V1_PREFIX)


# ------------------------------------------------------------------
# Root endpoints (outside /api/v1)
# ------------------------------------------------------------------
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint — confirms the API is online."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint.

    Returns service status with timestamp.  Used by load balancers,
    Docker health checks, and monitoring systems.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "debug": settings.DEBUG,
    }
