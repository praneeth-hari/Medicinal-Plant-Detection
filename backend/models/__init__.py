"""
Models package.

Import all models here so that ``Base.metadata`` is fully populated when
Alembic or the startup routine calls ``create_all``.
"""
from models.base import Base  # noqa: F401
from models.plant import Plant  # noqa: F401
from models.user import User  # noqa: F401
from models.chat import ChatSession, ChatMessage, MessageRole  # noqa: F401
from models.detection import DetectionResult  # noqa: F401

__all__ = [
    "Base",
    "Plant",
    "User",
    "ChatSession",
    "ChatMessage",
    "MessageRole",
    "DetectionResult",
]
