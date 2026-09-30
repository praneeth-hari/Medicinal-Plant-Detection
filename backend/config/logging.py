"""
Logging Configuration
=====================
Sets up structured logging for the application with both console
and optional file handlers.

Usage::

    from config.logging import setup_logging, get_logger

    setup_logging()
    logger = get_logger(__name__)
    logger.info("Application started")
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from config.settings import settings


def setup_logging() -> None:
    """Configure application-wide logging.

    Sets up:
    - Root logger level from ``settings.LOG_LEVEL``
    - Formatted console handler writing to stdout
    - Optional rotating file handler if ``settings.LOG_FILE`` is set
    - Quieter third-party loggers (uvicorn, sqlalchemy, httpx)
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates on reload
    root_logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler ──────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # ── File handler (optional) ──────────────────────────────────
    if settings.LOG_FILE:
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            str(log_path),
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # ── Quiet noisy third-party loggers ──────────────────────────
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        Configured ``logging.Logger`` instance.
    """
    return logging.getLogger(name)
