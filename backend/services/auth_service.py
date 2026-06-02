"""
Auth Service
============

Business-logic layer for user registration, authentication, and
JWT token management.  Delegates data access to ``UserRepository``.
"""

from __future__ import annotations

from typing import Optional

from repositories.user_repository import UserRepository
from schemas.user import Token, UserCreate, UserResponse


class AuthService:
    """Service encapsulating authentication and authorisation logic.

    Args:
        repository: Injected ``UserRepository`` instance.
    """

    def __init__(self, repository: UserRepository) -> None:
        """Initialise the service with a user repository.

        Args:
            repository: Data-access dependency.
        """
        self.repository = repository

    async def register(self, data: UserCreate) -> UserResponse:
        """Register a new user account.

        Validates uniqueness of username/email, hashes the password,
        and persists the new user.

        Args:
            data: Registration payload.

        Returns:
            Newly created ``UserResponse``.

        Raises:
            ValueError: If the username or email is already taken.
        """
        raise NotImplementedError("Not yet implemented")

    async def authenticate(self, username: str, password: str) -> Optional[UserResponse]:
        """Verify user credentials.

        Args:
            username: Login identifier (username or email).
            password: Plain-text password to check.

        Returns:
            ``UserResponse`` if credentials are valid, ``None`` otherwise.
        """
        raise NotImplementedError("Not yet implemented")

    async def create_token(self, user_id: int, username: str) -> Token:
        """Generate a JWT access token for an authenticated user.

        Args:
            user_id: The user's primary key (embedded as the ``sub`` claim).
            username: The user's display name (embedded as a custom claim).

        Returns:
            ``Token`` schema containing the encoded JWT.
        """
        raise NotImplementedError("Not yet implemented")
