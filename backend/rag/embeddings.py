"""
Embedding Service
=================

Generates dense vector embeddings from text using a sentence-transformer
model.  Supports single-text and batch embedding, as well as document
chunking for long-form content.

Uses ``all-MiniLM-L6-v2`` by default (384-dimensional embeddings,
fast and lightweight).
"""
from __future__ import annotations

import logging
import re
from typing import Sequence

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate vector embeddings from text using a sentence-transformer model.

    Lazy-loads the model on first use to avoid blocking application
    startup.

    Args:
        model_name: HuggingFace model identifier for the embedding model.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialise the embedding service.

        Args:
            model_name: Pre-trained sentence-transformer model name.
                        Defaults to ``all-MiniLM-L6-v2``.
        """
        self.model_name = model_name
        self._model = None
        self._dimension: int | None = None

    @property
    def model(self):
        """Lazy-load the sentence-transformer model."""
        if self._model is None:
            import sys
            from types import ModuleType

            # Mock blocked dll modules under Application Control Policies
            mock_name = "sklearn.metrics.cluster._expected_mutual_info_fast"
            if mock_name not in sys.modules:
                mock_mod = ModuleType(mock_name)
                mock_mod.expected_mutual_information = lambda *args, **kwargs: 0.0
                sys.modules[mock_name] = mock_mod

            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
            self._dimension = self._model.get_embedding_dimension()
            logger.info(
                "Embedding model loaded: dim=%d", self._dimension,
            )
        return self._model

    @property
    def dimension(self) -> int:
        """Return the embedding dimension, loading the model if needed."""
        if self._dimension is None:
            _ = self.model  # trigger lazy load
        return self._dimension  # type: ignore[return-value]

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a dense vector.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_documents(self, documents: Sequence[str]) -> list[list[float]]:
        """Embed multiple documents into dense vectors (batch mode).

        Args:
            documents: A sequence of text strings.

        Returns:
            A list of embedding vectors (one per document).
        """
        if not documents:
            return []
        embeddings = self.model.encode(
            list(documents), convert_to_numpy=True, show_progress_bar=False,
        )
        return embeddings.tolist()

    @staticmethod
    def chunk_text(
        text: str,
        *,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[str]:
        """Split text into overlapping chunks for embedding.

        Tries to break on sentence boundaries.  Falls back to
        character-level splitting if sentences are too long.

        Args:
            text: Full document text.
            chunk_size: Target characters per chunk.
            overlap: Character overlap between adjacent chunks.

        Returns:
            List of text chunks.
        """
        if len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks: list[str] = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Keep overlap from end of last chunk
                    if overlap > 0 and len(current_chunk) > overlap:
                        current_chunk = current_chunk[-overlap:] + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    # Single sentence exceeds chunk_size — force-split
                    for i in range(0, len(sentence), chunk_size - overlap):
                        chunks.append(sentence[i:i + chunk_size].strip())
                    current_chunk = ""

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks


# Module-level singleton
_embedding_service: EmbeddingService | None = None


def get_embedding_service(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingService:
    """Return a singleton ``EmbeddingService`` instance.

    Args:
        model_name: Model to use (only honoured on first call).

    Returns:
        Shared ``EmbeddingService``.
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(model_name)
    return _embedding_service
