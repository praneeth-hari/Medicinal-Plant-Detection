"""
Detection Schemas
=================
Pydantic models for plant image detection requests and responses.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PredictionItem(BaseModel):
    """A single prediction in the top-K results."""

    plant_id: Optional[int] = None
    name: str
    confidence: float = Field(ge=0.0, le=1.0)


class DetectionResponse(BaseModel):
    """Schema returned after a successful plant detection."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: Optional[int] = None
    plant_name: Optional[str] = None
    scientific_name: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    top_predictions: Optional[list[PredictionItem]] = None
    image_path: str
    model_version: str
    created_at: datetime


class DetectionHistoryResponse(BaseModel):
    """Paginated detection history."""

    items: list[DetectionResponse]
    total: int
    skip: int
    limit: int
