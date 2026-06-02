"""
RAG (Retrieval-Augmented Generation) package.

Houses the components of the RAG pipeline:

- **EmbeddingService**: Text → vector embeddings.
- **VectorStoreService**: ChromaDB wrapper for similarity search.
- **DocumentRetriever**: Retrieves relevant context from the vector store.
- **ResponseGenerator**: LLM-backed answer generation.
- **RAGPipeline**: Orchestrates retrieval + generation end-to-end.
"""
