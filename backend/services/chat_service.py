"""
Chat Service
============

Business-logic layer for the conversational RAG interface.  Manages
chat sessions, persists messages, and orchestrates the RAG pipeline
to generate assistant responses.
"""

from __future__ import annotations

from typing import Sequence

from repositories.chat_repository import ChatRepository
from schemas.chat import ChatMessageResponse, ChatResponse, ChatSessionResponse


class ChatService:
    """Service handling chat session management and RAG-powered responses.

    Args:
        repository: Injected ``ChatRepository`` instance.
    """

    def __init__(self, repository: ChatRepository) -> None:
        """Initialise the service with a chat repository.

        Args:
            repository: Data-access dependency.
        """
        self.repository = repository

    async def create_session(self, user_id: int, *, title: str | None = None) -> ChatSessionResponse:
        """Start a new chat session for a user.

        Args:
            user_id: Owner's user ID.
            title: Optional session title.

        Returns:
            ``ChatSessionResponse`` for the new session.
        """
        raise NotImplementedError("Not yet implemented")

    async def send_message(
        self,
        session_id: int,
        user_message: str,
        user_id: int,
    ) -> ChatResponse:
        """Process a user message and generate an assistant reply.

        Steps (to be implemented):
        1. Persist the user message.
        2. Retrieve relevant context via the RAG pipeline.
        3. Generate an assistant response.
        4. Persist the assistant message with source metadata.
        5. Return the ``ChatResponse``.

        Args:
            session_id: Chat session to append to.
            user_message: The user's natural-language query.
            user_id: Authenticated user's ID.

        Returns:
            ``ChatResponse`` containing the answer and sources.
        """
        raise NotImplementedError("Not yet implemented")

    async def get_history(
        self,
        session_id: int,
        *,
        skip: int = 0,
        limit: int = 200,
    ) -> Sequence[ChatMessageResponse]:
        """Retrieve the full message history for a session.

        Args:
            session_id: Chat session primary key.
            skip: Pagination offset.
            limit: Max messages.

        Returns:
            Sequence of ``ChatMessageResponse`` objects in chronological order.
        """
        raise NotImplementedError("Not yet implemented")

    async def get_user_sessions(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[ChatSessionResponse]:
        """List all chat sessions belonging to a user.

        Args:
            user_id: User's primary key.
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``ChatSessionResponse`` objects.
        """
        raise NotImplementedError("Not yet implemented")
