"""
Dependency Injection Helpers
============================

Central location for all FastAPI ``Depends()`` callables used across
endpoints.  This keeps dependency wiring out of endpoint files and
makes testing / overriding straightforward.
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from repositories.chat_repository import ChatRepository
from repositories.detection_repository import DetectionRepository
from repositories.plant_repository import PlantRepository
from repositories.user_repository import UserRepository
from schemas.user import TokenData
from services.auth_service import AuthService
from services.chat_service import ChatService
from services.detection_service import DetectionService
from services.plant_service import PlantService


# ------------------------------------------------------------------
# Database session (re-export for convenience)
# ------------------------------------------------------------------
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session.

    This is a thin wrapper around ``config.database.get_db`` so that
    endpoint code only needs to import from ``api.deps``.
    """
    async for session in get_db():
        yield session


# ------------------------------------------------------------------
# Repository factories
# ------------------------------------------------------------------
def get_plant_repository(
    session: AsyncSession = Depends(get_db),
) -> PlantRepository:
    """Provide a ``PlantRepository`` instance.

    Args:
        session: Injected database session.

    Returns:
        ``PlantRepository`` bound to the current session.
    """
    return PlantRepository(session)


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Provide a ``UserRepository`` instance.

    Args:
        session: Injected database session.

    Returns:
        ``UserRepository`` bound to the current session.
    """
    return UserRepository(session)


def get_chat_repository(
    session: AsyncSession = Depends(get_db),
) -> ChatRepository:
    """Provide a ``ChatRepository`` instance.

    Args:
        session: Injected database session.

    Returns:
        ``ChatRepository`` bound to the current session.
    """
    return ChatRepository(session)


def get_detection_repository(
    session: AsyncSession = Depends(get_db),
) -> DetectionRepository:
    """Provide a ``DetectionRepository`` instance.

    Args:
        session: Injected database session.

    Returns:
        ``DetectionRepository`` bound to the current session.
    """
    return DetectionRepository(session)


# ------------------------------------------------------------------
# Service factories
# ------------------------------------------------------------------
def get_plant_service(
    repo: PlantRepository = Depends(get_plant_repository),
) -> PlantService:
    """Provide a ``PlantService`` instance.

    Args:
        repo: Injected plant repository.

    Returns:
        ``PlantService`` wired to the repository.
    """
    return PlantService(repo)


def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Provide an ``AuthService`` instance.

    Args:
        repo: Injected user repository.

    Returns:
        ``AuthService`` wired to the repository.
    """
    return AuthService(repo)


def get_detection_service(
    repo: DetectionRepository = Depends(get_detection_repository),
) -> DetectionService:
    """Provide a ``DetectionService`` instance.

    Args:
        repo: Injected detection repository.

    Returns:
        ``DetectionService`` wired to the repository.
    """
    return DetectionService(repo)


def get_chat_service(
    repo: ChatRepository = Depends(get_chat_repository),
) -> ChatService:
    """Provide a ``ChatService`` instance.

    Args:
        repo: Injected chat repository.

    Returns:
        ``ChatService`` wired to the repository.
    """
    return ChatService(repo)


# ------------------------------------------------------------------
# Authentication dependency
# ------------------------------------------------------------------
async def get_current_user() -> TokenData:
    """Extract and validate the current user from the request's JWT.

    This is a placeholder that should be replaced with actual JWT
    decoding logic using ``python-jose`` and the application's
    ``SECRET_KEY``.

    Returns:
        ``TokenData`` with the authenticated user's claims.

    Raises:
        HTTPException: 401 if the token is missing or invalid.
    """
    raise NotImplementedError("Not yet implemented")
