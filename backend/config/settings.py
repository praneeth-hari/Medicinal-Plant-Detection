"""
Application Settings
====================
Centralised configuration loaded from environment variables / .env
via pydantic-settings.  All settings have sensible defaults for
local development.

Usage::

    from config.settings import settings
    print(settings.DATABASE_URL)
"""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings.

    Loaded from environment variables and a ``.env`` file.  Every
    field has a default suitable for local development.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "Medicinal Plant Detection & RAG Assistant"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./medicinal_plants.db"

    # --- Authentication / JWT ---
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- ML Model ---
    MODEL_PATH: str = "./data/models/plant_classifier.pth"

    # --- ChromaDB ---
    CHROMA_PERSIST_DIR: str = "./data/embeddings"

    # --- File Uploads ---
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    LOG_FILE: str | None = None

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    @property
    def upload_path(self) -> Path:
        """Resolved upload directory as a Path, created if absent."""
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_sqlite(self) -> bool:
        """Whether the configured database is SQLite."""
        return "sqlite" in self.DATABASE_URL


# Singleton — import this across the project.
settings = Settings()
