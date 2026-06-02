"""
Database Configuration
======================
Sets up the SQLAlchemy async engine, session factory, and declarative
base.  Exposes a FastAPI dependency ``get_db`` that yields an
``AsyncSession`` per request, plus ``init_db`` / ``close_db`` helpers.

Usage in endpoints::

    from config.database import get_db

    @router.get("/items")
    async def list_items(db: AsyncSession = Depends(get_db)):
        ...
"""
from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Engine — connection arguments differ for SQLite vs other DBs
# ------------------------------------------------------------------
_connect_args: dict = {}
if settings.is_sqlite:
    _connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    connect_args=_connect_args,
)

# ------------------------------------------------------------------
# Session factory
# ------------------------------------------------------------------
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ------------------------------------------------------------------
# Declarative Base
# ------------------------------------------------------------------
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    Every model in ``backend/models/`` should inherit from this class
    so that Alembic and the startup routine can discover its tables.
    """

    pass


# ------------------------------------------------------------------
# FastAPI dependency
# ------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session per request.

    Opens a session, yields it, then commits on success or rolls back
    on exception.  Always closes the session in the finally block.
    """
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("Database session rollback due to exception")
        raise
    finally:
        await session.close()


# ------------------------------------------------------------------
# Lifecycle helpers
# ------------------------------------------------------------------
async def init_db() -> None:
    """Create all database tables.

    For development convenience.  In production, use Alembic migrations.
    Must import all models *before* calling this so that
    ``Base.metadata`` is fully populated.
    """
    # Force-import the models package to populate Base.metadata
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified successfully")


async def close_db() -> None:
    """Dispose the database engine connection pool."""
    await engine.dispose()
    logger.info("Database engine disposed")
