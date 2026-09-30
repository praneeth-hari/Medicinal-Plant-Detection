"""
Chat Service
============

Business-logic layer for the conversational interface.  Manages
chat sessions, persists messages, and generates assistant responses
via the RAG pipeline (FAISS retrieval + Ollama generation).

Falls back to a graceful message when the RAG pipeline or Ollama
is unavailable.
"""
from __future__ import annotations

import aiofiles
import asyncio
import logging
import time
import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional, Sequence

from api.exceptions import ForbiddenException, NotFoundException
from models.chat import ChatMessage, ChatSession, MessageRole
from repositories.chat_repository import ChatRepository
from services import metrics
from schemas.chat import (
    ChatMessageResponse,
    ChatResponse,
    ChatSessionResponse,
)

logger = logging.getLogger(__name__)

# Queries showing intent to harm someone (or self). Deliberately narrower than a
# bare keyword list so legitimate safety questions ("Is neem toxic?", "Can tulsi
# poison a dog?") are still answered.
_TOXIC_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in (
        r"\b(kill|poison|murder|harm|hurt|killing|poisoning|murdering|hurting)\s+"
        r"(someone|somebody|a person|people|my\s+(wife|husband|partner|neighbou?r|boss|friend|mother|father|mom|dad|brother|sister|child|son|daughter|family|enemy|teacher|colleague)|him|her|them|a human)\b",
        r"\b(suicide|suicidal|self[- ]harm|kill myself|end my life)\b",
        r"\b(make|build|making|building)\s+(a\s+)?(bomb|explosive|weapon)s?\b",
        r"\bbomb\b",
        r"\bhate\s+(speech|crime)\b",
    )
]

_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
SETTINGS_PATH = os.path.join(_DATA_DIR, "control_tower_settings.json")
AUDIT_PATH = os.path.join(_DATA_DIR, "control_tower_audit_logs.json")

# Serialises read-modify-write of the audit log file across concurrent requests.
_AUDIT_LOCK = asyncio.Lock()

# Fallback when RAG pipeline is unavailable
_FALLBACK_RESPONSE = (
    "I'm unable to connect to the knowledge base or language model right now. "
    "Please ensure Ollama is running and the vector index has been built, "
    "then try again."
)


class ChatService:
    """Service handling chat session management and RAG-powered responses.

    Uses the RAG pipeline (FAISS retrieval + Ollama generation) when
    available.  Falls back to a graceful error message otherwise.

    Args:
        repository: Injected ``ChatRepository`` instance.
        rag_pipeline: Optional injected ``RAGPipeline`` instance.
    """

    def __init__(
        self,
        repository: ChatRepository,
        rag_pipeline: Optional[object] = None,
    ) -> None:
        """Initialise the service.

        Args:
            repository: Data-access dependency.
            rag_pipeline: Optional RAG pipeline for response generation.
        """
        self.repository = repository
        self._rag_pipeline = rag_pipeline

    @property
    def rag_pipeline(self):
        """Lazy-load the RAG pipeline if not injected."""
        if self._rag_pipeline is None:
            try:
                from rag.pipeline import get_rag_pipeline
                self._rag_pipeline = get_rag_pipeline()
            except Exception as e:
                logger.warning("RAG pipeline unavailable: %s", e)
        return self._rag_pipeline

    async def create_session(
        self, user_id: int, *, title: str | None = None,
    ) -> ChatSession:
        """Start a new chat session for a user.

        Args:
            user_id: Owner's user ID.
            title: Optional session title (defaults to "New Chat").

        Returns:
            ``ChatSession`` ORM model.
        """
        session_data = {
            "user_id": user_id,
            "title": title or "New Chat",
            "is_active": True,
        }
        session = await self.repository.create(session_data)
        logger.info("Created chat session id=%d for user=%d", session.id, user_id)
        return session

    async def send_message(
        self,
        session_id: int,
        user_message: str,
        user_id: int,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        """Process a user message and generate an assistant reply.

        Steps:
        1. Verify session exists and belongs to user.
        2. Persist the user message.
        3. Load chat history for multi-turn context.
        4. Generate response via RAG pipeline (or fallback).
        5. Persist the assistant message with sources.
        6. Return the ``ChatResponse``.

        Args:
            session_id: Chat session to append to.
            user_message: The user's natural-language query.
            user_id: Authenticated user's ID.

        Returns:
            ``ChatResponse`` containing the assistant's answer.

        Raises:
            NotFoundException: If the session does not exist.
            ForbiddenException: If the session belongs to another user.
        """
        # 1. Verify ownership
        session = await self._get_user_session(session_id, user_id)

        # Load control tower governance settings
        settings_path = SETTINGS_PATH
        pii_masking = False
        dosage_disclaimer = True
        toxicity_guardrail = True
        source_verification = True
        if os.path.exists(settings_path):
            try:
                async with aiofiles.open(settings_path, "r") as f:
                    raw = await f.read()
                    settings_data = json.loads(raw)
                    pii_masking = settings_data.get("pii_masking", False)
                    dosage_disclaimer = settings_data.get("dosage_disclaimer", True)
                    toxicity_guardrail = settings_data.get("toxicity_guardrail", True)
                    source_verification = settings_data.get("source_verification", True)
            except Exception:
                pass

        # Apply Toxicity Guardrail
        is_toxic = False
        policies_applied = []
        
        if toxicity_guardrail:
            policies_applied.append("Toxicity Guardrail")
            is_toxic = any(p.search(user_message) for p in _TOXIC_PATTERNS)

        # Apply PII Masking
        masked_message = user_message
        if pii_masking:
            policies_applied.append("PII Masking")
            # Email regex
            masked_message = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", masked_message)
            # Phone regex
            masked_message = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]", masked_message)
            # Patient ID regex
            masked_message = re.sub(r"\bPT-\d{4}\b", "[PATIENT_ID]", masked_message)

        # 2. Persist user message
        user_msg = await self.repository.create_message({
            "session_id": session_id,
            "role": MessageRole.USER,
            "content": user_message,
            "token_count": len(user_message.split()),
        })

        if is_toxic:
            assistant_content = "Your query was blocked by the safety guardrails due to toxicity concerns."
            sources = []
        else:
            # 3. Generate response via RAG pipeline
            started = time.perf_counter()
            assistant_content, sources = await self._generate_response(
                session_id, masked_message,
                temperature=temperature, max_tokens=max_tokens,
            )
            latency_ms = (time.perf_counter() - started) * 1000
            try:
                await asyncio.to_thread(
                    metrics.record, latency_ms,
                    len(user_message.split()) + len(assistant_content.split()),
                )
            except Exception as e:
                logger.warning("Failed to record chat metrics: %s", e)

        # Apply Dosage disclaimer
        dosage_keywords = ["dosage", "dose", "preparation", "preperation", "recipe", "quantity", "how to use", "how to prepare", "administration"]
        if not is_toxic and dosage_disclaimer:
            policies_applied.append("Dosage Guardrail")
            query_match = any(kw in user_message.lower() for kw in dosage_keywords)
            resp_match = any(kw in assistant_content.lower() for kw in dosage_keywords)
            if query_match or resp_match:
                assistant_content += "\n\n*⚠️ Disclaimer: Medicinal plant preparation and dosage recommendations are provided for informational purposes only. Please consult a qualified healthcare professional or herbalist before use.*"

        # Apply Source verification
        compliance_status = "PASSED"
        details = None
        if not is_toxic and source_verification:
            policies_applied.append("Source Verification")
            if not sources or len(sources) == 0:
                compliance_status = "WARNING"
                details = "No references or sources cited in the response."

        if is_toxic:
            compliance_status = "BLOCKED"
            details = "Query contains toxic keywords."

        # Write to compliance audit log
        audit_path = AUDIT_PATH
        audit_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_query": user_message,
            "masked_query": masked_message if pii_masking else None,
            "policies_applied": policies_applied,
            "compliance_status": compliance_status,
            "details": details
        }
        
        try:
            async with _AUDIT_LOCK:
                audit_logs = []
                if os.path.exists(audit_path):
                    async with aiofiles.open(audit_path, "r") as f:
                        raw = await f.read()
                        audit_logs = json.loads(raw)
                audit_logs.insert(0, audit_entry)
                audit_logs = audit_logs[:100]
                async with aiofiles.open(audit_path, "w") as f:
                    await f.write(json.dumps(audit_logs, indent=2))
        except Exception as e:
            logger.warning("Failed to save control tower audit logs: %s", e)

        # 4. Persist assistant message
        assistant_msg = await self.repository.create_message({
            "session_id": session_id,
            "role": MessageRole.ASSISTANT,
            "content": assistant_content,
            "sources": sources,
            "token_count": len(assistant_content.split()),
        })

        # 5. Update session title from first user message
        msg_count = await self.repository.count_messages(session_id)
        if msg_count <= 2:
            title = user_message[:50].strip()
            if len(user_message) > 50:
                title += "..."
            await self.repository.update(session_id, {"title": title})

        logger.info(
            "Chat exchange in session=%d: user_msg=%d, assistant_msg=%d",
            session_id, user_msg.id, assistant_msg.id,
        )

        # 6. Return response
        return ChatResponse(
            session_id=session_id,
            message=ChatMessageResponse.model_validate(assistant_msg),
        )

    async def _generate_response(
        self,
        session_id: int,
        user_message: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[str, list[dict]]:
        """Generate an assistant response via the RAG pipeline.

        Falls back to a graceful message if the pipeline is
        unavailable.

        Args:
            session_id: Current session for history lookup.
            user_message: The user's query.

        Returns:
            Tuple of (response_text, sources_list).
        """
        pipeline = self.rag_pipeline
        if pipeline is None:
            return _FALLBACK_RESPONSE, []

        try:
            # Build chat history from prior messages (skip=1 to exclude the current user message
            # which was just persisted, preventing it from appearing twice in the LLM context)
            history_msgs = await self.repository.get_messages_by_session(
                session_id, skip=0, limit=20,
            )
            # Exclude the very last message (current user message just added)
            history_msgs = list(history_msgs)[:-1] if history_msgs else []
            chat_history = [
                {"role": m.role.value, "content": m.content}
                for m in history_msgs
            ]

            # Run the pipeline with history
            if chat_history:
                result = await pipeline.answer_with_history(
                    user_message, chat_history,
                    top_k=5, max_tokens=max_tokens or 512, temperature=temperature,
                )
            else:
                result = await pipeline.answer(
                    user_message,
                    top_k=5, max_tokens=max_tokens or 512, temperature=temperature,
                )

            answer = result.get("answer", _FALLBACK_RESPONSE)
            sources = result.get("sources", [])
            return answer, sources

        except Exception as e:
            logger.exception("RAG pipeline error: %s", e)
            return _FALLBACK_RESPONSE, []

    async def get_history(
        self,
        session_id: int,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 200,
    ) -> Sequence[ChatMessage]:
        """Retrieve the full message history for a session.

        Verifies that the session belongs to the requesting user.

        Args:
            session_id: Chat session primary key.
            user_id: Authenticated user's ID.
            skip: Pagination offset.
            limit: Max messages.

        Returns:
            Sequence of ``ChatMessage`` ORM models in chronological order.

        Raises:
            NotFoundException: If the session does not exist.
            ForbiddenException: If the session belongs to another user.
        """
        await self._get_user_session(session_id, user_id)
        return await self.repository.get_messages_by_session(
            session_id, skip=skip, limit=limit,
        )

    async def get_user_sessions(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ChatSessionResponse]:
        """List all chat sessions belonging to a user.

        Enriches each session with its message count.

        Args:
            user_id: User's primary key.
            skip: Offset.
            limit: Max results.

        Returns:
            List of ``ChatSessionResponse`` objects.
        """
        sessions = await self.repository.get_sessions_by_user(
            user_id, skip=skip, limit=limit,
        )
        result = []
        for s in sessions:
            msg_count = await self.repository.count_messages(s.id)
            resp = ChatSessionResponse(
                id=s.id,
                title=s.title,
                is_active=s.is_active,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=msg_count,
            )
            result.append(resp)
        return result

    async def _get_user_session(
        self, session_id: int, user_id: int,
    ) -> ChatSession:
        """Retrieve a session and verify ownership.

        Args:
            session_id: Chat session primary key.
            user_id: Expected owner.

        Returns:
            ``ChatSession`` if valid.

        Raises:
            NotFoundException: If session does not exist.
            ForbiddenException: If session belongs to another user.
        """
        session = await self.repository.get(session_id)
        if session is None:
            raise NotFoundException("Chat session", session_id)
        if session.user_id != user_id:
            raise ForbiddenException("You do not own this chat session")
        return session
