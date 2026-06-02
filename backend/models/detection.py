"""
Detection Result Model
======================
SQLAlchemy ORM model recording the outcome of a plant identification
request, linking the uploaded image to the predicted plant and user.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class DetectionResult(Base):
    """Persisted result of a plant image classification.

    Records the user, identified plant, confidence, and the full
    list of top-K predictions from the ML model.

    Attributes:
        id: Primary key.
        user_id: Foreign key → users.id (nullable for anonymous).
        plant_id: Foreign key → plants.id (nullable if unknown).
        image_path: Path to the uploaded image on disk.
        confidence: Model confidence score (0.0–1.0).
        model_version: Identifier for the model checkpoint used.
        top_predictions: JSON array of top-K predictions.
        created_at: When the detection was performed.
    """

    __tablename__ = "detection_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    plant_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("plants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    model_version: Mapped[str] = mapped_column(
        String(50), nullable=False, default="v1.0.0"
    )
    top_predictions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # --- Relationships ---
    user: Mapped["User | None"] = relationship(  # noqa: F821
        "User", back_populates="detection_results"
    )
    plant: Mapped["Plant | None"] = relationship(  # noqa: F821
        "Plant", back_populates="detection_results"
    )

    def __repr__(self) -> str:
        return (
            f"<DetectionResult(id={self.id}, plant_id={self.plant_id}, "
            f"confidence={self.confidence:.2f})>"
        )
