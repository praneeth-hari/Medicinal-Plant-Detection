"""
Chat Repository
===============

Data-access layer for ``ChatSession`` and ``ChatMessage`` entities.
Inherits generic CRUD (scoped to ``ChatSession``) from ``BaseRepository``
and adds dedicated methods for message management and user-scoped queries.
"""
from __future__ import annotations

import logging
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.chat import ChatMessage, ChatSession, MessageRole
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ChatRepository(BaseRepository[ChatSession]):
    """Repository for chat sessions and their messages.

    While the generic base is typed to ``ChatSession``, this repository
    also manages ``ChatMessage`` records through dedicated methods.

    Attributes:
        model: The ``ChatSession`` ORM class.
    """

    model = ChatSession

    def __init__(self, session: AsyncSession) -> None:
        """Initialise with an async database session.

        Args:
            session: SQLAlchemy ``AsyncSession``.
        """
        super().__init__(session)

    # ---- Chat-specific queries ----

    async def get_sessions_by_user(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[ChatSession]:
        """List all chat sessions belonging to a specific user.

        Returns sessions in reverse chronological order (newest first).

        Args:
            user_id: Owner's user ID.
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``ChatSession`` instances.
        """
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_session_for_user(
        self, session_id: int, user_id: int,
    ) -> Optional[ChatSession]:
        """Retrieve a chat session only if it belongs to the given user.

        Args:
            session_id: ChatSession primary key.
            user_id: Expected owner.

        Returns:
            ``ChatSession`` if found and owned by user, else ``None``.
        """
        stmt = (
            select(ChatSession)
            .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_messages_by_session(
        self,
        session_id: int,
        *,
        skip: int = 0,
        limit: int = 200,
    ) -> Sequence[ChatMessage]:
        """Retrieve all messages in a given session, ordered chronologically.

        Args:
            session_id: ChatSession primary key.
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``ChatMessage`` instances.
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_message(self, obj_in: dict) -> ChatMessage:
        """Append a new message to a chat session.

        Args:
            obj_in: Column data (session_id, role, content, sources, token_count).

        Returns:
            Newly created ``ChatMessage``.
        """
        db_msg = ChatMessage(**obj_in)
        self.session.add(db_msg)
        await self.session.flush()
        await self.session.refresh(db_msg)
        logger.debug(
            "Created ChatMessage(id=%s, role=%s, session=%s)",
            db_msg.id, db_msg.role, db_msg.session_id,
        )
        return db_msg

    async def count_messages(self, session_id: int) -> int:
        """Count the number of messages in a session.

        Args:
            session_id: ChatSession primary key.

        Returns:
            Message count.
        """
        stmt = (
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.session_id == session_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
