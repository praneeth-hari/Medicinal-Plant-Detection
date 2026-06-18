"""
User Repository
===============

Data-access layer for ``User`` entities.  Extends the generic
``BaseRepository`` with user-specific lookup methods for
authentication (by email, by username).
"""
from __future__ import annotations

import logging
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository handling all database operations for users.

    Inherits generic CRUD from ``BaseRepository`` and adds
    user-specific lookups.

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

    # ---- User-specific queries ----

    async def get_by_email(self, email: str) -> Optional[User]:
        """Look up a user by their email address (case-insensitive).

        Args:
            email: Email to search for.

        Returns:
            ``User`` instance or ``None``.
        """
        stmt = select(User).where(func.lower(User.email) == email.lower())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Look up a user by their username (case-insensitive).

        Args:
            username: Username to search for.

        Returns:
            ``User`` instance or ``None``.
        """
        stmt = select(User).where(func.lower(User.username) == username.lower())
        result = await self.session.execute(stmt)
        return result.scalars().first()
