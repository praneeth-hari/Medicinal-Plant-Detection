"""
User Model
==========
SQLAlchemy ORM model for the ``users`` table — stores registered
user accounts with hashed passwords and relationships to chat
sessions and detection results.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class User(Base):
    """Application user account.

    Attributes:
        id: Primary key.
        username: Unique display name (3–50 chars, alphanumeric).
        email: Unique email address.
        hashed_password: Bcrypt-hashed password (never store plaintext).
        is_active: Soft-delete / deactivation flag.
        created_at: Row creation timestamp.
        updated_at: Last modification timestamp.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Relationships ---
    chat_sessions: Mapped[list["ChatSession"]] = relationship(  # noqa: F821
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    detection_results: Mapped[list["DetectionResult"]] = relationship(  # noqa: F821
        "DetectionResult",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
