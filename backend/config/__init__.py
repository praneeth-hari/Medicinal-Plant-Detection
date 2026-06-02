"""
Configuration package for Medicinal Plant Detection & RAG Assistant.

Exports:
    - Settings: Application settings loaded from environment / .env file.
    - engine: SQLAlchemy async engine instance.
    - async_session_maker: Async session factory.
    - Base: Declarative base class for ORM models.
    - get_db: FastAPI dependency that yields a database session.
"""
