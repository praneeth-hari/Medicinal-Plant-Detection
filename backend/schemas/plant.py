"""
Plant Schemas
=============
Pydantic models for validating and serialising Plant data across
the API boundary.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PlantBase(BaseModel):
    """Shared fields common to all plant schemas."""

    common_name: str = Field(
        ..., min_length=1, max_length=200, examples=["Tulsi"]
    )
    scientific_name: str = Field(
        ..., min_length=1, max_length=200, examples=["Ocimum tenuiflorum"]
    )
    family: Optional[str] = Field(
        None, max_length=100, examples=["Lamiaceae"]
    )
    description: Optional[str] = Field(
        None, examples=["Holy basil, a sacred plant in Hinduism..."]
    )
    medicinal_uses: Optional[str] = Field(
        None, examples=["Used for treating cough, cold, fever, respiratory disorders..."]
    )
    habitat: Optional[str] = Field(
        None, examples=["Tropical and subtropical regions of Asia"]
    )
    image_url: Optional[str] = Field(None, max_length=500)
    preparation_methods: Optional[str] = Field(
        None, examples=["Leaves can be consumed raw, as tea, or as extract..."]
    )
    precautions: Optional[str] = Field(
        None, examples=["May interact with blood-thinning medications..."]
    )


class PlantCreate(PlantBase):
    """Schema for creating a new plant record.

    Inherits all fields from ``PlantBase``; no additional fields
    needed for creation.
    """

    pass


class PlantUpdate(BaseModel):
    """Schema for partially updating a plant record.

    All fields are optional (PATCH semantics) so callers can send
    only the fields they wish to change.
    """

    common_name: Optional[str] = Field(None, min_length=1, max_length=200)
    scientific_name: Optional[str] = Field(None, min_length=1, max_length=200)
    family: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    medicinal_uses: Optional[str] = None
    habitat: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    preparation_methods: Optional[str] = None
    precautions: Optional[str] = None


class PlantResponse(PlantBase):
    """Schema returned to clients when reading plant data.

    Includes server-generated fields such as ``id`` and timestamps.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PlantListResponse(BaseModel):
    """Paginated list of plants."""

    items: list[PlantResponse]
    total: int
    skip: int
    limit: int
