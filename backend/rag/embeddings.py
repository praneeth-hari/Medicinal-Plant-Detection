"""
Embedding Service
=================

Wrapper around a sentence-transformer model for converting text into
dense vector embeddings suitable for similarity search.
"""

from __future__ import annotations

from typing import Sequence


class EmbeddingService:
    """Generate vector embeddings from text using a sentence-transformer model.

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
        # TODO: Load the model here.
        #   from sentence_transformers import SentenceTransformer
        #   self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a dense vector.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        raise NotImplementedError("Not yet implemented")

    def embed_documents(self, documents: Sequence[str]) -> list[list[float]]:
        """Embed multiple documents into dense vectors (batch mode).

        Args:
            documents: A sequence of text strings.

        Returns:
            A list of embedding vectors (one per document).
        """
        raise NotImplementedError("Not yet implemented")
