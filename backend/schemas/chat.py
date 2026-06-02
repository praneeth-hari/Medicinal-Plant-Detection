"""
Chat Schemas
============

Pydantic models for chat requests, responses, session listings, and
individual message serialisation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the client.

    Attributes:
        session_id: Existing session to continue (``None`` to start a new one).
        message: The user's natural-language question.
    """

    session_id: Optional[int] = None
    message: str = Field(..., min_length=1, max_length=4096)


class ChatResponse(BaseModel):
    """Response returned after processing a chat message.

    Attributes:
        session_id: The session this message belongs to.
        answer: The assistant's generated answer.
        sources: Optional list of source references used by the RAG pipeline.
    """

    session_id: int
    answer: str
    sources: Optional[list[dict[str, Any]]] = None


class ChatMessageResponse(BaseModel):
    """Schema for an individual stored chat message.

    Attributes:
        id: Message primary key.
        role: ``user``, ``assistant``, or ``system``.
        content: Message body.
        sources: RAG source metadata (if any).
        created_at: Timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    sources: Optional[dict[str, Any]] = None
    created_at: datetime


class ChatSessionResponse(BaseModel):
    """Schema for a chat session summary (list view).

    Attributes:
        id: Session primary key.
        title: Session title.
        created_at: When the session was created.
        message_count: Number of messages in the session.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Optional[str] = None
    created_at: datetime
    message_count: int = 0
