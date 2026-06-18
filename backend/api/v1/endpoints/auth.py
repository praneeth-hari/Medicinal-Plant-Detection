"""
Auth Endpoints
==============

Authentication API endpoints for user registration, login, and
profile retrieval.

Routes:
    POST  /register — Register a new user account.
    POST  /login    — Authenticate and obtain a JWT access token.
    GET   /me       — Retrieve the current user's profile.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, status

from api.deps import get_auth_service, get_current_user
from api.exceptions import NotFoundException
from schemas.user import Token, UserCreate, UserLogin, UserResponse, TokenData, ChangePasswordRequest
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register",
    description="Create a new user account.",
)
async def register(
    user_in: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user.

    Args:
        user_in: Registration payload (username, email, password).
        service: Injected ``AuthService``.

    Returns:
        Newly created ``UserResponse``.

    Raises:
        AlreadyExistsException: 409 if username or email already exists.
    """
    user = await service.register(user_in)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate with email and password to receive a JWT.",
)
async def login(
    credentials: UserLogin,
    service: AuthService = Depends(get_auth_service),
) -> Token:
    """Authenticate a user and return a JWT.

    Uses the ``UserLogin`` JSON body with ``email`` and ``password``
    fields.

    Args:
        credentials: Login payload with email and password.
        service: Injected ``AuthService``.

    Returns:
        ``Token`` containing the JWT access token.

    Raises:
        UnauthorizedException: 401 if credentials are invalid.
    """
    user = await service.authenticate(credentials.email, credentials.password)
    token = await service.create_token(user.id, user.username, user.role)
    return token


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
)
async def change_password(
    body: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.change_password(current_user.user_id, body.current_password, body.new_password)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Current user",
    description="Retrieve the authenticated user's profile.",
)
async def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Retrieve the current authenticated user's profile.

    Args:
        current_user: Token data from the JWT (injected via Depends).
        service: Injected ``AuthService``.

    Returns:
        ``UserResponse`` with the user's profile data.

    Raises:
        NotFoundException: 404 if the user no longer exists.
    """
    user = await service.get_user_by_id(current_user.user_id)
    if user is None:
        raise NotFoundException("User", current_user.user_id)
    return UserResponse.model_validate(user)
