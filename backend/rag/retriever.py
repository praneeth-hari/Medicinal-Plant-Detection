"""
Document Retriever
==================

Retrieves the most relevant context documents from the FAISS vector
store given a user query, formats them into a prompt-ready context
block, and converts results to source reference dicts.
"""
from __future__ import annotations

import logging
from typing import Any

from rag.embeddings import EmbeddingService
from rag.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Retrieve and format relevant documents for the RAG pipeline.

    Args:
        vector_store: An initialised ``VectorStoreService`` instance.
        embedding_service: An ``EmbeddingService`` for query embedding.
    """

    def __init__(
        self,
        vector_store: VectorStoreService,
        embedding_service: EmbeddingService,
    ) -> None:
        """Initialise with a vector store and embedding dependency.

        Args:
            vector_store: The vector store to query.
            embedding_service: Service for generating query embeddings.
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve the top-K most relevant documents for a query.

        Embeds the query, searches the FAISS index, re-ranks based on
        query keyword boosts, applies duplicate suppression per plant,
        and returns the top results.
        """
        if not self.vector_store.is_loaded:
            logger.warning("Vector store is empty — no documents to retrieve")
            return []

        # 1. Fetch more results initially to allow for filtering/re-ranking
        initial_k = max(top_k * 2, 10)
        query_embedding = self.embedding_service.embed_text(query)
        results = self.vector_store.search(query_embedding, n_results=initial_k)

        if not results:
            return []

        # 2. Metadata-Aware Re-ranking / Keyword Boosting
        # Parse query for plant names
        query_lower = query.lower()
        plant_names = [
            "tulsi", "neem", "ashwagandha", "aloe vera", "brahmi", "turmeric", "amla", 
            "mint", "curry leaves", "hibiscus", "ginger", "garlic", "moringa", "lemongrass", 
            "shatavari", "giloy", "arjuna", "bael", "bhringraj", "fenugreek"
        ]
        
        detected_plants = []
        for name in plant_names:
            if name in query_lower:
                detected_plants.append(name)

        # If a plant is detected, boost its score
        for r in results:
            meta = r.get("metadata", {})
            plant = str(meta.get("plant", "")).lower()
            source = str(meta.get("source", "")).lower()
            
            # Direct match boost
            boosted = False
            for dp in detected_plants:
                if dp in plant or dp in source:
                    r["score"] += 0.25  # Apply score boost
                    boosted = True
            
            # Give a minor penalty for general pages if specific is queried
            if detected_plants and not boosted:
                r["score"] -= 0.1

        # Re-sort results based on boosted scores
        results.sort(key=lambda x: x["score"], reverse=True)

        # 3. Duplicate Suppression (max 2 chunks per plant)
        final_results = []
        plant_counts = {}
        max_chunks_per_plant = 2

        for r in results:
            meta = r.get("metadata", {})
            plant = meta.get("plant", "unknown")
            
            count = plant_counts.get(plant, 0)
            if count < max_chunks_per_plant:
                final_results.append(r)
                plant_counts[plant] = count + 1
            
            if len(final_results) >= top_k:
                break

        # If we suppressed too many and have less than top_k, fill up with remaining unique chunks if possible
        if len(final_results) < top_k and len(final_results) < len(results):
            for r in results:
                if r not in final_results:
                    final_results.append(r)
                if len(final_results) >= top_k:
                    break

        logger.info(
            "Retrieved %d docs (suppressed/boosted from %d) for query: '%s...' (top score: %.3f)",
            len(final_results),
            len(results),
            query[:50],
            final_results[0]["score"] if final_results else 0.0,
        )
        return final_results

    @staticmethod
    def format_context(documents: list[dict[str, Any]]) -> str:
        """Format retrieved documents into a single context string.

        The output is suitable for injection into an LLM prompt as
        grounding context.

        Args:
            documents: Result dictionaries from ``retrieve()``.

        Returns:
            A formatted multi-document context string.
        """
        if not documents:
            return "No relevant documents found in the knowledge base."

        parts: list[str] = []
        for i, doc in enumerate(documents, 1):
            meta = doc.get("metadata", {})
            source = meta.get("source", "Unknown")
            score = doc.get("score", 0.0)
            text = doc.get("document", "")
            parts.append(
                f"[Source {i}] ({source}, relevance: {score:.2f})\n{text}"
            )
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def to_source_references(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert retrieval results to source reference dicts for the API.

        Args:
            documents: Result dictionaries from ``retrieve()``.

        Returns:
            List of source reference dicts with ``document``, ``page``,
            ``relevance_score``, and ``snippet`` keys.
        """
        sources = []
        for doc in documents:
            meta = doc.get("metadata", {})
            sources.append({
                "document": meta.get("source", "knowledge_base"),
                "page": meta.get("chunk_index", None),
                "relevance_score": round(doc.get("score", 0.0), 4),
                "snippet": doc.get("document", "")[:200],
            })
        return sources
