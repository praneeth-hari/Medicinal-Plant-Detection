"""
Chat Endpoints
==============

API endpoints for the RAG-powered chat assistant.

Routes:
    POST  /                  — Send a message and get an AI response.
    GET   /sessions          — List the user's chat sessions.
    GET   /sessions/{id}     — Retrieve messages for a specific session.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from api.deps import get_chat_service, get_current_user
from schemas.chat import ChatMessageResponse, ChatRequest, ChatResponse, ChatSessionResponse
from schemas.user import TokenData
from services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message",
    description="Send a message to the RAG assistant and receive an answer.",
)
async def send_message(
    body: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Process a user message through the RAG pipeline.

    Args:
        body: Chat request with session_id and message text.
        current_user: Authenticated user's token data.
        service: Injected ``ChatService``.

    Returns:
        ``ChatResponse`` with the assistant's answer and sources.
    """
    raise NotImplementedError("Not yet implemented")


@router.get(
    "/sessions",
    response_model=list[ChatSessionResponse],
    summary="List sessions",
    description="Retrieve all chat sessions for the current user.",
)
async def list_sessions(
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(50, ge=1, le=200, description="Max sessions to return"),
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> list[ChatSessionResponse]:
    """List the current user's chat sessions.

    Args:
        skip: Pagination offset.
        limit: Page size.
        current_user: Authenticated user's token data.
        service: Injected ``ChatService``.

    Returns:
        List of ``ChatSessionResponse`` objects.
    """
    raise NotImplementedError("Not yet implemented")


@router.get(
    "/sessions/{session_id}",
    response_model=list[ChatMessageResponse],
    summary="Get session messages",
    description="Retrieve the message history for a specific chat session.",
)
async def get_session_messages(
    session_id: int,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(200, ge=1, le=1000, description="Max messages to return"),
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> list[ChatMessageResponse]:
    """Retrieve all messages in a chat session.

    Args:
        session_id: Chat session primary key.
        skip: Pagination offset.
        limit: Page size.
        current_user: Authenticated user's token data.
        service: Injected ``ChatService``.

    Returns:
        List of ``ChatMessageResponse`` objects.
    """
    raise NotImplementedError("Not yet implemented")
