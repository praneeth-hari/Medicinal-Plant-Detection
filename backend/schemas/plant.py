"""
Plant Schemas
=============
Pydantic models for validating and serialising Plant data across
the API boundary.

Schema tiers
------------
PlantResponse       — legacy flat-text response; all existing API endpoints
                      and frontend components use this. Never remove fields.
PlantDetailResponse — full structured evidence response; returned by the
                      /plants/{id}/detail endpoint once a plant has been
                      through the evidence migration (evidence_strength != NULL).
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


# ── Structured evidence response ──────────────────────────────────────────────

def _parse_json_list(v: Any) -> list:
    """Deserialise a JSON string to a list; return [] on failure."""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        try:
            result = json.loads(v)
            return result if isinstance(result, list) else []
        except (json.JSONDecodeError, ValueError):
            return []
    return []


class PlantDetailResponse(PlantResponse):
    """
    Full structured evidence response for a single plant.

    Extends PlantResponse (keeps all legacy fields intact) and adds
    the evidence columns added in migration 0002.

    Returned only when evidence_strength is not NULL — i.e., the plant
    has been through the pilot evidence conversion.

    JSON text columns are automatically deserialised to Python lists.
    """

    model_config = ConfigDict(from_attributes=True)

    # ── Evidence: indexed ─────────────────────────────────────────────────────
    evidence_strength: Optional[str] = None
    safety_class:      Optional[str] = None
    review_status:     Optional[str] = None

    # ── Evidence: plain text ──────────────────────────────────────────────────
    native_region:     Optional[str] = None
    last_reviewed:     Optional[str] = None
    traditional_uses:  Optional[str] = None
    evidence_summary:  Optional[str] = None
    reviewer_notes:    Optional[str] = None
    overdose_risk:     Optional[str] = None

    # ── Evidence: JSON arrays (deserialised automatically) ────────────────────
    local_names:                     list[Any] = Field(default_factory=list)
    traditional_systems:             list[Any] = Field(default_factory=list)
    regulatory_status:               list[Any] = Field(default_factory=list)
    therapeutic_claims:              list[Any] = Field(default_factory=list)
    drug_interactions:               list[Any] = Field(default_factory=list)
    safety_warnings:                 list[Any] = Field(default_factory=list)
    active_compounds:                list[Any] = Field(default_factory=list)
    dosage_info:                     list[Any] = Field(default_factory=list)
    preparation_methods_structured:  list[Any] = Field(default_factory=list)
    citation_flags:                  list[Any] = Field(default_factory=list)
    flagged_issues:                  list[Any] = Field(default_factory=list)

    # ── Evidence: booleans ────────────────────────────────────────────────────
    who_monograph_available:   bool = False
    ayush_monograph_available: bool = False

    # ── Validators: deserialise JSON text columns from ORM ────────────────────
    @field_validator(
        "local_names", "traditional_systems", "regulatory_status",
        "therapeutic_claims", "drug_interactions", "safety_warnings",
        "active_compounds", "dosage_info", "preparation_methods_structured",
        "citation_flags", "flagged_issues",
        mode="before",
    )
    @classmethod
    def _deserialise_json(cls, v: Any) -> list:
        return _parse_json_list(v)

    @field_validator("who_monograph_available", "ayush_monograph_available", mode="before")
    @classmethod
    def _coerce_bool(cls, v: Any) -> bool:
        return bool(v)
