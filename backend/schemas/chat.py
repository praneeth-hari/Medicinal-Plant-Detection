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
    """Incoming chat message from the client."""

    session_id: Optional[int] = Field(
        None, description="Existing session to continue (null to start new)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="The user's natural-language question",
    )
    temperature: Optional[float] = Field(
        None, ge=0.0, le=1.2, description="LLM sampling temperature (default 0.3)"
    )
    max_tokens: Optional[int] = Field(
        None, ge=128, le=4096, description="Max tokens in the generated answer (default 512)"
    )


class SourceReference(BaseModel):
    """A single RAG source reference."""

    document: str = Field(description="Source document name")
    page: Optional[int] = Field(None, description="Page number if applicable")
    relevance_score: float = Field(description="Retrieval relevance score")
    snippet: str = Field(description="Relevant text snippet")


class ChatMessageResponse(BaseModel):
    """Schema for an individual stored chat message."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    sources: Optional[list[dict[str, Any]]] = None
    token_count: Optional[int] = None
    created_at: datetime


class ChatResponse(BaseModel):
    """Response returned after processing a chat message."""

    session_id: int
    message: ChatMessageResponse


class ChatSessionResponse(BaseModel):
    """Schema for a chat session summary (list view)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ChatSessionDetailResponse(BaseModel):
    """Full chat session with all messages."""

    session: ChatSessionResponse
    messages: list[ChatMessageResponse]
