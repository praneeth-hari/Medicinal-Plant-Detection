"""
Plant Model
===========
SQLAlchemy ORM model for the ``plants`` table — stores comprehensive
data about medicinal plants including botanical classification,
medicinal properties, and usage information.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Plant(Base):
    """Medicinal plant information.

    Stores comprehensive data about a medicinal plant including
    botanical classification, medicinal properties, and usage info.

    Attributes:
        id: Primary key.
        common_name: Commonly used name of the plant.
        scientific_name: Binomial nomenclature (unique).
        family: Botanical family the plant belongs to.
        description: Free-text description of the plant.
        medicinal_uses: Known medicinal applications.
        habitat: Typical growing environment / geography.
        image_url: URL or path to a representative image.
        preparation_methods: How to prepare for medicinal use.
        precautions: Warnings and contraindications.
        created_at: Row creation timestamp (server-side default).
        updated_at: Last modification timestamp (auto-updated).
    """

    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    common_name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    scientific_name: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True, index=True
    )
    family: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    medicinal_uses: Mapped[str | None] = mapped_column(Text, nullable=True)
    habitat: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    preparation_methods: Mapped[str | None] = mapped_column(Text, nullable=True)
    precautions: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    detection_results: Mapped[list["DetectionResult"]] = relationship(  # noqa: F821
        "DetectionResult",
        back_populates="plant",
    )

    def __repr__(self) -> str:
        return f"<Plant(id={self.id}, scientific_name='{self.scientific_name}')>"
