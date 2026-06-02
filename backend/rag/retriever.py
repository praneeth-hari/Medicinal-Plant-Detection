"""
Document Retriever
==================

Retrieves the most relevant context documents from the vector store
given a user query, and formats them into a prompt-ready context block.
"""

from __future__ import annotations

from typing import Any

from rag.vector_store import VectorStoreService


class DocumentRetriever:
    """Retrieve and format relevant documents for the RAG pipeline.

    Args:
        vector_store: An initialised ``VectorStoreService`` instance.
    """

    def __init__(self, vector_store: VectorStoreService) -> None:
        """Initialise with a vector store dependency.

        Args:
            vector_store: The vector store to query.
        """
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve the top-K most relevant documents for a query.

        Args:
            query: Natural-language user query.
            top_k: Number of documents to retrieve.

        Returns:
            List of result dictionaries from the vector store.
        """
        raise NotImplementedError("Not yet implemented")

    def format_context(self, documents: list[dict[str, Any]]) -> str:
        """Format retrieved documents into a single context string.

        The output is suitable for injection into an LLM prompt as
        grounding context.

        Args:
            documents: Result dictionaries from ``retrieve()``.

        Returns:
            A formatted multi-document context string.
        """
        raise NotImplementedError("Not yet implemented")
