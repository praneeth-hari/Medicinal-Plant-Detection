"""
RAG Pipeline
=============

End-to-end orchestrator that wires together the ``DocumentRetriever``
and ``ResponseGenerator`` to answer user questions about medicinal
plants using retrieval-augmented generation.
"""

from __future__ import annotations

from typing import Any, Optional

from rag.retriever import DocumentRetriever
from rag.generator import ResponseGenerator


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
        raise NotImplementedError("Not yet implemented")

    async def answer_with_history(
        self,
        query: str,
        chat_history: list[dict[str, str]],
        *,
        top_k: int = 5,
        max_tokens: int = 512,
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
        raise NotImplementedError("Not yet implemented")
