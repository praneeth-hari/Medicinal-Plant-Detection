"""
Plant Model
===========

SQLAlchemy ORM model representing a medicinal plant and its associated
metadata.  This is the core domain entity of the application.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Plant(Base):
    """Medicinal plant information.

    Attributes:
        id: Primary key.
        common_name: Commonly used name of the plant.
        scientific_name: Binomial nomenclature (unique).
        family: Botanical family the plant belongs to.
        description: Free-text description of the plant.
        medicinal_uses: Known medicinal applications.
        habitat: Typical growing environment / geography.
        image_url: URL or path to a representative image.
        created_at: Row creation timestamp (server-side default).
        updated_at: Last modification timestamp (auto-updated).
    """

    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    common_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scientific_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    family: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    medicinal_uses: Mapped[str | None] = mapped_column(Text, nullable=True)
    habitat: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
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

    def __repr__(self) -> str:
        return f"<Plant(id={self.id}, scientific_name='{self.scientific_name}')>"
