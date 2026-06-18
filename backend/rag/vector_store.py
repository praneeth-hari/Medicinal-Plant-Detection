"""
Vector Store Service
====================

FAISS-based vector store for persisting and querying document
embeddings.  Supports index creation, persistence to disk,
loading from disk, and similarity search with metadata.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional, Sequence

import numpy as np

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Manage a FAISS index for similarity-based retrieval.

    Stores documents, metadata, and the FAISS index.  Index and
    metadata are persisted to disk as ``index.faiss`` and
    ``metadata.json`` in the configured directory.

    Args:
        persist_directory: Filesystem path for index persistence.
        collection_name: Logical name (used in file naming).
    """

    def __init__(
        self,
        persist_directory: str = "./data/embeddings",
        collection_name: str = "medicinal_plants",
    ) -> None:
        """Initialise the vector store.

        Args:
            persist_directory: Path for index persistence.
            collection_name: Logical collection name.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._index = None
        self._documents: list[str] = []
        self._metadatas: list[dict[str, Any]] = []
        self._ids: list[str] = []

    @property
    def index_path(self) -> str:
        """Path to the FAISS index file."""
        return os.path.join(
            self.persist_directory, f"{self.collection_name}.faiss",
        )

    @property
    def metadata_path(self) -> str:
        """Path to the metadata JSON file."""
        return os.path.join(
            self.persist_directory, f"{self.collection_name}_meta.json",
        )

    @property
    def is_loaded(self) -> bool:
        """Whether an index is currently loaded in memory."""
        return self._index is not None and len(self._documents) > 0

    @property
    def count(self) -> int:
        """Number of documents in the store."""
        return len(self._documents)

    def create_index(
        self,
        embeddings: list[list[float]],
        documents: Sequence[str],
        metadatas: Optional[Sequence[dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> None:
        """Create a FAISS index from pre-computed embeddings.

        Builds a flat L2 index, stores documents and metadata,
        and persists everything to disk.

        Args:
            embeddings: List of embedding vectors (one per document).
            documents: Text content of the documents.
            metadatas: Per-document metadata dictionaries.
            ids: Unique identifiers for each document.
        """
        import faiss

        if not embeddings:
            logger.warning("create_index called with empty embeddings")
            return

        dimension = len(embeddings[0])
        vectors = np.array(embeddings, dtype=np.float32)

        # Normalise for cosine similarity via inner product
        faiss.normalize_L2(vectors)
        index = faiss.IndexFlatIP(dimension)
        index.add(vectors)

        self._index = index
        self._documents = list(documents)
        self._metadatas = list(metadatas) if metadatas else [{} for _ in documents]
        self._ids = list(ids) if ids else [str(i) for i in range(len(documents))]

        # Persist
        self._save_index()
        logger.info(
            "Created FAISS index: %d docs, dim=%d, path=%s",
            len(documents), dimension, self.index_path,
        )

    def load_index(self) -> bool:
        """Load a previously persisted FAISS index from disk.

        Returns:
            ``True`` if the index was loaded successfully,
            ``False`` if the files do not exist.
        """
        import faiss

        if not os.path.exists(self.index_path):
            logger.warning("No FAISS index at %s", self.index_path)
            return False
        if not os.path.exists(self.metadata_path):
            logger.warning("No metadata at %s", self.metadata_path)
            return False

        self._index = faiss.read_index(self.index_path)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._documents = data.get("documents", [])
        self._metadatas = data.get("metadatas", [])
        self._ids = data.get("ids", [])

        logger.info(
            "Loaded FAISS index: %d docs from %s",
            len(self._documents), self.index_path,
        )
        return True

    def add_documents(
        self,
        embeddings: list[list[float]],
        documents: Sequence[str],
        metadatas: Optional[Sequence[dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> None:
        """Add documents to an existing index.

        If no index exists yet, creates one.

        Args:
            embeddings: Embedding vectors for new documents.
            documents: Text content of the documents.
            metadatas: Per-document metadata dictionaries.
            ids: Unique identifiers for each document.
        """
        if self._index is None:
            self.create_index(embeddings, documents, metadatas, ids)
            return

        import faiss

        vectors = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(vectors)
        self._index.add(vectors)

        self._documents.extend(documents)
        self._metadatas.extend(metadatas if metadatas else [{} for _ in documents])
        offset = len(self._ids)
        self._ids.extend(ids if ids else [str(offset + i) for i in range(len(documents))])

        self._save_index()
        logger.info("Added %d docs to index (total: %d)", len(documents), len(self._documents))

    def search(
        self,
        query_embedding: list[float],
        *,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Perform a similarity search against the index.

        Args:
            query_embedding: Embedding vector for the query.
            n_results: Number of top results to return.

        Returns:
            List of result dictionaries containing ``document``,
            ``metadata``, ``id``, and ``score`` keys.
        """
        import faiss

        if self._index is None or self._index.ntotal == 0:
            logger.warning("Search called on empty or unloaded index")
            return []

        query_vec = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_vec)

        k = min(n_results, self._index.ntotal)
        scores, indices = self._index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._documents):
                continue
            results.append({
                "document": self._documents[idx],
                "metadata": self._metadatas[idx],
                "id": self._ids[idx],
                "score": float(score),
            })
        return results

    def delete_collection(self) -> None:
        """Delete the index and metadata files from disk.

        Also clears in-memory state.
        """
        for path in [self.index_path, self.metadata_path]:
            if os.path.exists(path):
                os.remove(path)
                logger.info("Deleted %s", path)

        self._index = None
        self._documents = []
        self._metadatas = []
        self._ids = []

    def _save_index(self) -> None:
        """Persist the FAISS index and metadata to disk."""
        import faiss

        os.makedirs(self.persist_directory, exist_ok=True)
        faiss.write_index(self._index, self.index_path)

        meta = {
            "documents": self._documents,
            "metadatas": self._metadatas,
            "ids": self._ids,
        }
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)


# Module-level singleton
_vector_store: VectorStoreService | None = None


def get_vector_store(
    persist_directory: str = "./data/embeddings",
    collection_name: str = "medicinal_plants",
) -> VectorStoreService:
    """Return a singleton ``VectorStoreService``, loading from disk if available.

    Args:
        persist_directory: Path for index persistence.
        collection_name: Logical collection name.

    Returns:
        Shared ``VectorStoreService``.
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService(persist_directory, collection_name)
        _vector_store.load_index()  # Load if exists, otherwise stays empty
    return _vector_store
