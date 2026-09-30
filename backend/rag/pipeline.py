"""
RAG Pipeline
=============

End-to-end orchestrator that wires together the ``DocumentRetriever``
and ``ResponseGenerator`` to answer user questions about medicinal
plants using retrieval-augmented generation.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from rag.retriever import DocumentRetriever
from rag.generator import ResponseGenerator

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Orchestrate the full retrieve → generate pipeline.

    Args:
        retriever: Handles document retrieval from the vector store.
        generator: Handles answer generation from an LLM.
    """

    def __init__(
        self,
        retriever: DocumentRetriever,
        generator: ResponseGenerator,
    ) -> None:
        """Initialise the pipeline with its two core components.

        Args:
            retriever: ``DocumentRetriever`` instance.
            generator: ``ResponseGenerator`` instance.
        """
        self.retriever = retriever
        self.generator = generator

    async def answer(
        self,
        query: str,
        *,
        top_k: int = 5,
        max_tokens: int = 512,
        temperature: Optional[float] = None,
    ) -> dict[str, Any]:
        """Run the full RAG pipeline for a user query.

        Steps:
        1. Retrieve the top-K relevant documents.
        2. Format them into a context block.
        3. Generate an LLM answer grounded in that context.
        4. Return the answer along with source metadata.

        Args:
            query: User's natural-language question.
            top_k: Number of documents to retrieve.
            max_tokens: Max tokens for the generated answer.

        Returns:
            Dictionary with keys ``answer`` (str) and ``sources``
            (list of source metadata dicts).
        """
        # 1. Retrieve
        documents = self.retriever.retrieve(query, top_k=top_k)

        # 2. Format context
        context = self.retriever.format_context(documents)

        # 3. Generate
        answer_text = await self.generator.generate(
            query, context, max_tokens=max_tokens, temperature=temperature,
        )

        # 4. Build sources
        sources = self.retriever.to_source_references(documents)

        logger.info(
            "RAG pipeline: query='%s...' docs=%d answer_len=%d",
            query[:40], len(documents), len(answer_text),
        )
        return {"answer": answer_text, "sources": sources}

    async def answer_with_history(
        self,
        query: str,
        chat_history: list[dict[str, str]],
        *,
        top_k: int = 5,
        max_tokens: int = 512,
        temperature: Optional[float] = None,
    ) -> dict[str, Any]:
        """Run the RAG pipeline while incorporating chat history.

        This variant allows the pipeline to consider prior conversation
        turns for more coherent multi-turn dialogues.

        Args:
            query: Current user question.
            chat_history: List of prior messages, each a dict with
                          ``role`` and ``content`` keys.
            top_k: Number of documents to retrieve.
            max_tokens: Max generated tokens.

        Returns:
            Dictionary with ``answer`` and ``sources``.
        """
        # 1. Retrieve (based on current query only)
        documents = self.retriever.retrieve(query, top_k=top_k)

        # 2. Format context
        context = self.retriever.format_context(documents)

        # 3. Generate with history
        answer_text = await self.generator.generate(
            query, context,
            max_tokens=max_tokens,
            temperature=temperature,
            chat_history=chat_history,
        )

        # 4. Build sources
        sources = self.retriever.to_source_references(documents)

        logger.info(
            "RAG pipeline (with history): query='%s...' docs=%d history=%d",
            query[:40], len(documents), len(chat_history),
        )
        return {"answer": answer_text, "sources": sources}


# ── Module-level singleton ──────────────────────────────────────

_pipeline: RAGPipeline | None = None


def get_rag_pipeline() -> RAGPipeline:
    """Return a singleton ``RAGPipeline`` wired with default components.

    Lazy-initialises the embedding service, vector store, retriever,
    and generator on first call.

    Returns:
        Shared ``RAGPipeline`` instance.
    """
    global _pipeline
    if _pipeline is None:
        from config.settings import settings
        from rag.embeddings import get_embedding_service
        from rag.vector_store import get_vector_store

        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        retriever = DocumentRetriever(vector_store, embedding_service)
        generator = ResponseGenerator(
            model_name=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

        _pipeline = RAGPipeline(retriever, generator)
        logger.info("RAG pipeline initialised with Ollama model %s", settings.OLLAMA_MODEL)
    return _pipeline
