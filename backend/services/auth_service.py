"""
Auth Service
============

Business-logic layer for user registration, authentication, and
JWT token management.  Delegates data access to ``UserRepository``
and uses ``passlib`` for password hashing and ``python-jose`` for
JWT encoding.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt

from api.exceptions import AlreadyExistsException, UnauthorizedException
from config.settings import settings
from models.user import User
from repositories.user_repository import UserRepository
from schemas.user import Token, UserCreate

logger = logging.getLogger(__name__)


class AuthService:
    """Service encapsulating authentication and authorisation logic.

    Provides user registration (with duplicate checking), credential
    verification, and JWT access-token generation.

    Args:
        repository: Injected ``UserRepository`` instance.
    """

    def __init__(self, repository: UserRepository) -> None:
        """Initialise the service with a user repository.

        Args:
            repository: Data-access dependency.
        """
        self.repository = repository

    # ── Password utilities ────────────────────────────────────────

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hash a plain-text password using bcrypt.

        Truncates to 72 bytes (bcrypt limit) before hashing.

        Args:
            plain_password: The raw password string.

        Returns:
            Bcrypt-hashed password string.
        """
        # Bcrypt only processes the first 72 bytes
        pw_bytes = plain_password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pw_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a bcrypt hash.

        Args:
            plain_password: The raw password to check.
            hashed_password: The stored bcrypt hash.

        Returns:
            ``True`` if the password matches.
        """
        pw_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)

    # ── Registration ──────────────────────────────────────────────

    async def register(self, data: UserCreate) -> User:
        """Register a new user account.

        Validates uniqueness of username and email, hashes the
        password, and persists the new user.

        Args:
            data: Registration payload (username, email, password).

        Returns:
            Newly created ``User`` ORM model.

        Raises:
            AlreadyExistsException: If the username or email is taken.
        """
        # Check for existing username
        existing_user = await self.repository.get_by_username(data.username)
        if existing_user is not None:
            raise AlreadyExistsException("User", "username")

        # Check for existing email
        existing_email = await self.repository.get_by_email(data.email)
        if existing_email is not None:
            raise AlreadyExistsException("User", "email")

        # Create user with hashed password
        user_data = {
            "username": data.username,
            "email": data.email.lower().strip(),
            "hashed_password": self.hash_password(data.password),
            "is_active": True,
            "role": data.role if hasattr(data, "role") else "customer",
        }
        user = await self.repository.create(user_data)
        logger.info("Registered new user: %s (id=%d)", user.username, user.id)
        return user

    # ── Authentication ────────────────────────────────────────────

    async def authenticate(self, email: str, password: str) -> User:
        """Verify user credentials by email and password.

        Args:
            email: The user's email address.
            password: Plain-text password to check.

        Returns:
            ``User`` ORM model if credentials are valid.

        Raises:
            UnauthorizedException: If email is not found or password
                does not match.
        """
        user = await self.repository.get_by_email(email)
        if user is None:
            # Don't reveal whether the email exists
            raise UnauthorizedException("Invalid email or password")

        if not self.verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        logger.info("User authenticated: %s (id=%d)", user.username, user.id)
        return user

    # ── JWT Token ─────────────────────────────────────────────────

    async def create_token(self, user_id: int, username: str, role: str = "customer") -> Token:
        """Generate a JWT access token for an authenticated user.

        The token contains:
        - ``sub``: User's primary key (as string, per JWT convention).
        - ``username``: User's display name.
        - ``exp``: Expiration timestamp.

        Args:
            user_id: The user's primary key.
            username: The user's display name.

        Returns:
            ``Token`` schema containing the encoded JWT.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        logger.debug("JWT created for user_id=%d, expires=%s", user_id, expire)
        return Token(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    # ── User lookup ───────────────────────────────────────────────

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        user = await self.repository.get(user_id)
        if user is None:
            raise UnauthorizedException("User not found")
        if not self.verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")
        await self.repository.update(user_id, {"hashed_password": self.hash_password(new_password)})
        logger.info("Password changed for user_id=%d", user_id)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their primary key.

        Args:
            user_id: User's primary key.

        Returns:
            ``User`` ORM model or ``None``.
        """
        return await self.repository.get(user_id)
