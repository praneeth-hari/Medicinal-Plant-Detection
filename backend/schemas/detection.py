"""
Detection Schemas
=================

Pydantic models for plant image detection requests and responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DetectionRequest(BaseModel):
    """Schema representing the metadata sent alongside an uploaded image.

    The actual image binary is received via ``UploadFile``; this schema
    captures any extra form fields.

    Attributes:
        model_version: Optional model checkpoint identifier the client
                       wants to use.  Defaults to the latest available.
    """

    model_version: Optional[str] = Field(None, max_length=100)


class DetectionResponse(BaseModel):
    """Schema returned after a successful plant detection.

    Attributes:
        id: Detection result primary key.
        plant_id: Predicted plant's ID (``None`` if unknown).
        plant_name: Predicted plant's common name.
        scientific_name: Predicted plant's scientific name.
        confidence: Model confidence score (0.0–1.0).
        image_path: Server-side path to the stored image.
        model_version: Model checkpoint used for this prediction.
        created_at: Detection timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: Optional[int] = None
    plant_name: Optional[str] = None
    scientific_name: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    image_path: str
    model_version: Optional[str] = None
    created_at: datetime
