"""
Detection Result Model
======================

SQLAlchemy ORM model recording the outcome of a plant identification
request, linking the uploaded image to the predicted plant and user.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class DetectionResult(Base):
    """Persisted result of a plant image classification.

    Attributes:
        id: Primary key.
        user_id: Foreign key → users.id (who submitted the image).
        plant_id: Foreign key → plants.id (predicted plant, nullable if unknown).
        image_path: Path to the uploaded image on disk.
        confidence: Model confidence score (0.0 – 1.0).
        model_version: Identifier for the model checkpoint used.
        created_at: When the detection was performed.
    """

    __tablename__ = "detection_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plant_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("plants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship("User", back_populates="detection_results")  # noqa: F821
    plant: Mapped["Plant | None"] = relationship("Plant")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<DetectionResult(id={self.id}, plant_id={self.plant_id}, "
            f"confidence={self.confidence})>"
        )
