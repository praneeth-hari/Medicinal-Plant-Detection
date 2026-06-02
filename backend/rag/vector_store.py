"""
Vector Store Service
====================

Thin abstraction over ChromaDB for persisting and querying document
embeddings.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence


class VectorStoreService:
    """Manage a ChromaDB collection for similarity-based retrieval.

    Args:
        persist_directory: Filesystem path where ChromaDB persists data.
        collection_name: Name of the ChromaDB collection to use.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_data",
        collection_name: str = "medicinal_plants",
    ) -> None:
        """Initialise the vector store and obtain a collection handle.

        Args:
            persist_directory: Path for ChromaDB persistence.
            collection_name: Logical collection name.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        # TODO: Initialise ChromaDB client and collection.
        #   import chromadb
        #   self.client = chromadb.PersistentClient(path=persist_directory)
        #   self.collection = self.client.get_or_create_collection(collection_name)

    def add_documents(
        self,
        documents: Sequence[str],
        metadatas: Optional[Sequence[dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> None:
        """Add documents (with optional metadata) to the collection.

        Args:
            documents: Text content of the documents.
            metadatas: Per-document metadata dictionaries.
            ids: Unique identifiers for each document.
        """
        raise NotImplementedError("Not yet implemented")

    def search(
        self,
        query: str,
        *,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Perform a similarity search against the collection.

        Args:
            query: Natural-language query string.
            n_results: Number of top results to return.

        Returns:
            List of result dictionaries containing document content,
            metadata, and distance scores.
        """
        raise NotImplementedError("Not yet implemented")

    def delete_collection(self) -> None:
        """Delete the entire ChromaDB collection.

        Use with caution — this is irreversible.
        """
        raise NotImplementedError("Not yet implemented")
