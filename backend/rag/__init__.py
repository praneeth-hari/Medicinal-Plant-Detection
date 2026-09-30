"""
RAG (Retrieval-Augmented Generation) package.

Houses the components of the RAG pipeline:

- **EmbeddingService**: Text → vector embeddings.
- **VectorStoreService**: FAISS wrapper for similarity search.
- **DocumentRetriever**: Retrieves relevant context from the vector store.
- **ResponseGenerator**: Ollama-backed answer generation.
- **RAGPipeline**: Orchestrates retrieval + generation end-to-end.
"""
