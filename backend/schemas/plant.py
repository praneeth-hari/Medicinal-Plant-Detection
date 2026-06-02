"""
Plant Schemas
=============

Pydantic models for validating and serialising Plant data across the
API boundary.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PlantBase(BaseModel):
    """Shared fields common to all plant schemas.

    Attributes:
        common_name: Commonly used name of the plant.
        scientific_name: Binomial nomenclature.
        family: Botanical family.
        description: Free-text description.
        medicinal_uses: Known medicinal applications.
        habitat: Typical growing environment.
        image_url: URL or path to a representative image.
    """

    common_name: str = Field(..., min_length=1, max_length=255, examples=["Tulsi"])
    scientific_name: str = Field(..., min_length=1, max_length=255, examples=["Ocimum tenuiflorum"])
    family: Optional[str] = Field(None, max_length=255, examples=["Lamiaceae"])
    description: Optional[str] = None
    medicinal_uses: Optional[str] = None
    habitat: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)


class PlantCreate(PlantBase):
    """Schema for creating a new plant record.

    Inherits all fields from ``PlantBase``; no additional fields needed
    for creation.
    """

    pass


class PlantUpdate(BaseModel):
    """Schema for partially updating a plant record.

    All fields are optional so that callers can send only the fields
    they wish to change (PATCH semantics).
    """

    common_name: Optional[str] = Field(None, min_length=1, max_length=255)
    scientific_name: Optional[str] = Field(None, min_length=1, max_length=255)
    family: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    medicinal_uses: Optional[str] = None
    habitat: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)


class PlantResponse(PlantBase):
    """Schema returned to clients when reading plant data.

    Includes server-generated fields such as ``id`` and timestamps.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
