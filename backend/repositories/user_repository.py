"""
User Repository
===============

Data-access layer for ``User`` entities.  Extends the generic
``BaseRepository`` with user-specific lookup methods.
"""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling all database operations for users.

    Attributes:
        model: The ``User`` ORM class managed by this repository.
    """

    model = User

    def __init__(self, session: AsyncSession) -> None:
        """Initialise with an async database session.

        Args:
            session: SQLAlchemy ``AsyncSession``.
        """
        super().__init__(session)

    # ---- BaseRepository CRUD stubs ----

    async def get(self, id: int) -> Optional[User]:
        """Retrieve a user by primary key.

        Args:
            id: User primary key.

        Returns:
            ``User`` instance or ``None``.
        """
        raise NotImplementedError("Not yet implemented")

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Retrieve a paginated list of users.

        Args:
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``User`` instances.
        """
        raise NotImplementedError("Not yet implemented")

    async def create(self, obj_in: dict) -> User:
        """Create a new user record.

        Args:
            obj_in: Column data (should include hashed_password, not plaintext).

        Returns:
            Newly created ``User``.
        """
        raise NotImplementedError("Not yet implemented")

    async def update(self, id: int, obj_in: dict) -> Optional[User]:
        """Update an existing user record.

        Args:
            id: User primary key.
            obj_in: Fields to update.

        Returns:
            Updated ``User`` or ``None``.
        """
        raise NotImplementedError("Not yet implemented")

    async def delete(self, id: int) -> bool:
        """Delete a user record (hard delete).

        Args:
            id: User primary key.

        Returns:
            ``True`` if deleted.
        """
        raise NotImplementedError("Not yet implemented")

    # ---- User-specific queries ----

    async def get_by_email(self, email: str) -> Optional[User]:
        """Look up a user by their email address.

        Args:
            email: Email to search for.

        Returns:
            ``User`` instance or ``None``.
        """
        raise NotImplementedError("Not yet implemented")

    async def get_by_username(self, username: str) -> Optional[User]:
        """Look up a user by their username.

        Args:
            username: Username to search for.

        Returns:
            ``User`` instance or ``None``.
        """
        raise NotImplementedError("Not yet implemented")
