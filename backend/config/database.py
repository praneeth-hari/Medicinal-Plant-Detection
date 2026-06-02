"""
Database Configuration
======================

Sets up the SQLAlchemy **async** engine, session factory, and declarative
base class.  Also exposes a FastAPI dependency (``get_db``) that yields an
``AsyncSession`` per request.

Usage in endpoints::

    from config.database import get_db

    @router.get("/items")
    async def list_items(db: AsyncSession = Depends(get_db)):
        ...
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings

# ------------------------------------------------------------------
# Engine
# ------------------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
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
    """Yield an async database session and ensure it is closed afterwards.

    This is the canonical FastAPI dependency for database access.  It
    opens a session at the start of a request and commits / rolls back
    automatically when the request finishes.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
