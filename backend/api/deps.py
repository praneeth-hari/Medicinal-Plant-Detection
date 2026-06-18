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
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException
from api.exceptions import UnauthorizedException
from config.database import get_db
from config.settings import settings
from repositories.chat_repository import ChatRepository
from repositories.detection_repository import DetectionRepository
from repositories.plant_repository import PlantRepository
from repositories.user_repository import UserRepository
from schemas.user import TokenData
from services.auth_service import AuthService
from services.chat_service import ChatService
from services.detection_service import DetectionService
from services.plant_service import PlantService

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme (optional — allows Swagger "Authorize" button)
security = HTTPBearer(auto_error=False)


# ══════════════════════════════════════════════════════════════════
# Repository factories
# ══════════════════════════════════════════════════════════════════

def get_plant_repository(
    session: AsyncSession = Depends(get_db),
) -> PlantRepository:
    """Provide a ``PlantRepository`` bound to the current session."""
    return PlantRepository(session)


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Provide a ``UserRepository`` bound to the current session."""
    return UserRepository(session)


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


def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Provide an ``AuthService`` wired to its repository."""
    return AuthService(repo)


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
# Authentication dependencies
# ══════════════════════════════════════════════════════════════════

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> TokenData:
    """Extract and validate the current user from the request's JWT.

    Decodes the Bearer token from the ``Authorization`` header,
    validates its claims, and returns a ``TokenData`` object.

    Args:
        credentials: HTTP Bearer credentials from the request header.

    Returns:
        ``TokenData`` with the authenticated user's claims.

    Raises:
        UnauthorizedException: If token is missing, expired, or invalid.
    """
    if credentials is None:
        raise UnauthorizedException("Authentication required")

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: int | None = payload.get("sub")
        username: str | None = payload.get("username")
        role: str = payload.get("role", "customer")

        if user_id is None:
            raise UnauthorizedException("Invalid token: missing subject")

        return TokenData(user_id=int(user_id), username=username, role=role)

    except JWTError as e:
        logger.warning("JWT validation failed: %s", e)
        raise UnauthorizedException("Invalid or expired token")


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """Ensure the current user is active."""
    return current_user


async def require_developer(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """Restrict an endpoint to users with the 'developer' role.

    Raises:
        HTTPException 403: If the authenticated user is not a developer.
    """
    if current_user.role != "developer":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Developer role required.",
        )
    return current_user
