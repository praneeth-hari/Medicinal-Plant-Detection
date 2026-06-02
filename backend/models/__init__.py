"""
Models package for Medicinal Plant Detection & RAG Assistant.

Import all models here so that ``Base.metadata`` is fully populated when
Alembic or the startup routine calls ``create_all``.

Exports:
    - Base: Declarative base (from config.database).
    - Plant: Plant information model.
    - User: User account model.
    - ChatSession, ChatMessage: Conversational history models.
    - DetectionResult: Image detection result model.
"""

from models.base import Base  # noqa: F401
from models.plant import Plant  # noqa: F401
from models.user import User  # noqa: F401
from models.chat import ChatSession, ChatMessage  # noqa: F401
from models.detection import DetectionResult  # noqa: F401
