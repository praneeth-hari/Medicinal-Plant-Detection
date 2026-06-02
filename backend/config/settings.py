"""
Application Settings
====================

Centralised configuration loaded from environment variables and a ``.env``
file via *pydantic-settings*.  All settings have sensible defaults suitable
for local development; override them in the environment or ``.env`` for
staging / production.

Usage::

    from config.settings import settings
    print(settings.DATABASE_URL)
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings.

    Attributes:
        DATABASE_URL: SQLAlchemy async connection string.
        SECRET_KEY: Secret used for signing JWT tokens.
        ALGORITHM: JWT signing algorithm (default: HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: Token lifetime in minutes.
        MODEL_PATH: Filesystem path to the plant classification model.
        CHROMA_PERSIST_DIR: Directory where ChromaDB persists data.
        UPLOAD_DIR: Directory for user-uploaded images.
        DEBUG: Enable debug-level logging and development helpers.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # --- Database ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./medicinal_plants.db"

    # --- Authentication / JWT ---
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- ML Model ---
    MODEL_PATH: str = "./ml_models/plant_classifier"

    # --- ChromaDB ---
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # --- File Uploads ---
    UPLOAD_DIR: str = "./uploads"

    # --- Debug ---
    DEBUG: bool = True


# Singleton instance — import this across the project.
settings = Settings()
