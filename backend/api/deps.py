"""
Dependency Injection Helpers
============================

Central location for all FastAPI ``Depends()`` callables used across
endpoints.  This keeps dependency wiring out of endpoint files and
makes testing / overriding straightforward.
"""
from __future__ import annotations

import logging

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from repositories.chat_repository import ChatRepository
from repositories.detection_repository import DetectionRepository
from repositories.plant_repository import PlantRepository
from schemas.user import TokenData
from services.chat_service import ChatService
from services.detection_service import DetectionService
from services.plant_service import PlantService

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════
# Repository factories
# ══════════════════════════════════════════════════════════════════

def get_plant_repository(
    session: AsyncSession = Depends(get_db),
) -> PlantRepository:
    """Provide a ``PlantRepository`` bound to the current session."""
    return PlantRepository(session)


def get_chat_repository(
    session: AsyncSession = Depends(get_db),
) -> ChatRepository:
    """Provide a ``ChatRepository`` bound to the current session."""
    return ChatRepository(session)


def get_detection_repository(
    session: AsyncSession = Depends(get_db),
) -> DetectionRepository:
    """Provide a ``DetectionRepository`` bound to the current session."""
    return DetectionRepository(session)


# ══════════════════════════════════════════════════════════════════
# Service factories
# ══════════════════════════════════════════════════════════════════

def get_plant_service(
    repo: PlantRepository = Depends(get_plant_repository),
) -> PlantService:
    """Provide a ``PlantService`` wired to its repository."""
    return PlantService(repo)


def get_detection_service(
    repo: DetectionRepository = Depends(get_detection_repository),
) -> DetectionService:
    """Provide a ``DetectionService`` wired to its repository."""
    return DetectionService(repo)


def get_chat_service(
    repo: ChatRepository = Depends(get_chat_repository),
) -> ChatService:
    """Provide a ``ChatService`` wired to its repository."""
    return ChatService(repo)


# ══════════════════════════════════════════════════════════════════
# Current user (no login)
# ══════════════════════════════════════════════════════════════════

# The app has no login system: every request acts as this single local user,
# which is created at startup (see ``ensure_local_user`` in ``main.py``).
LOCAL_USER_ID = 1
LOCAL_USERNAME = "local"


async def get_current_user() -> TokenData:
    """Return the single local user that all requests act as."""
    return TokenData(user_id=LOCAL_USER_ID, username=LOCAL_USERNAME)
