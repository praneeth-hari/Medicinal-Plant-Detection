"""
Chat Endpoints
==============

API endpoints for the chat assistant.

Routes:
    POST  /                  — Send a message and get a response.
    GET   /sessions          — List the user's chat sessions.
    GET   /sessions/{id}     — Retrieve messages for a specific session.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query, status

from api.deps import get_chat_service, get_current_user
from schemas.chat import (
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    ChatSessionResponse,
)
from schemas.user import TokenData
from services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message",
    description="Send a message to the assistant and receive an answer.",
)
async def send_message(
    body: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Process a user message through the chat service.

    If ``session_id`` is ``null``, a new session is created
    automatically.

    Args:
        body: Chat request with optional session_id and message text.
        current_user: Authenticated user's token data.
        service: Injected ``ChatService``.

    Returns:
        ``ChatResponse`` with the assistant's answer and sources.
    """
    # Auto-create session if none provided
    session_id = body.session_id
    if session_id is None:
        session = await service.create_session(current_user.user_id)
        session_id = session.id

    response = await service.send_message(
        session_id=session_id,
        user_message=body.message,
        user_id=current_user.user_id,
    )
    return response


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
    return await service.get_user_sessions(
        current_user.user_id, skip=skip, limit=limit,
    )


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

    Verifies that the session belongs to the authenticated user.

    Args:
        session_id: Chat session primary key.
        skip: Pagination offset.
        limit: Page size.
        current_user: Authenticated user's token data.
        service: Injected ``ChatService``.

    Returns:
        List of ``ChatMessageResponse`` objects.

    Raises:
        NotFoundException: 404 if the session does not exist.
        ForbiddenException: 403 if the session belongs to another user.
    """
    messages = await service.get_history(
        session_id, current_user.user_id, skip=skip, limit=limit,
    )
    return [ChatMessageResponse.model_validate(m) for m in messages]
