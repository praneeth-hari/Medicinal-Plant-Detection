"""
Auth Endpoints
==============

Authentication API endpoints for user registration and login.

Routes:
    POST  /register — Register a new user account.
    POST  /login    — Authenticate and obtain a JWT access token.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_auth_service
from schemas.user import Token, UserCreate, UserResponse
from services.auth_service import AuthService

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
        HTTPException: 409 if username or email already exists.
    """
    raise NotImplementedError("Not yet implemented")


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate with username and password to receive a JWT.",
)
async def login(
    username: str,
    password: str,
    service: AuthService = Depends(get_auth_service),
) -> Token:
    """Authenticate a user and return a JWT.

    Args:
        username: Login identifier.
        password: Plain-text password.
        service: Injected ``AuthService``.

    Returns:
        ``Token`` containing the JWT access token.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    raise NotImplementedError("Not yet implemented")
