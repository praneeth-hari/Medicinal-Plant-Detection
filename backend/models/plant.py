"""
Plant Model
===========
SQLAlchemy ORM model for the ``plants`` table — stores comprehensive
data about medicinal plants including botanical classification,
medicinal properties, and usage information.

Column groups
-------------
Legacy (flat text)  — original fields; preserved for frontend compatibility.
Evidence (indexed)  — evidence_strength, safety_class, review_status; written
                      from computed EvidenceBasedPlant fields; indexed for
                      filtering without loading JSON blobs.
Evidence (JSON)     — structured sub-model arrays stored as JSON text.
Evidence (meta)     — dates, booleans, plain-text summaries.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Plant(Base):
    __tablename__ = "plants"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Core identity ─────────────────────────────────────────────────────────
    common_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    scientific_name: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True, index=True
    )
    family: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # ── Legacy flat-text fields (preserved — frontend reads these) ─────────────
    description: Mapped[str | None]          = mapped_column(Text, nullable=True)
    medicinal_uses: Mapped[str | None]       = mapped_column(Text, nullable=True)
    habitat: Mapped[str | None]              = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None]            = mapped_column(String(500), nullable=True)
    preparation_methods: Mapped[str | None]  = mapped_column(Text, nullable=True)
    precautions: Mapped[str | None]          = mapped_column(Text, nullable=True)

    # ── Evidence: indexed filterable columns ──────────────────────────────────
    # Written from computed EvidenceBasedPlant fields at seed/write time.
    # Never set directly — always derived by the Pydantic model_validator first.
    evidence_strength: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    safety_class: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    review_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )

    # ── Evidence: plain text / date ───────────────────────────────────────────
    native_region: Mapped[str | None]  = mapped_column(String(300), nullable=True)
    last_reviewed: Mapped[str | None]  = mapped_column(String(10),  nullable=True)
    traditional_uses: Mapped[str | None]  = mapped_column(Text, nullable=True)
    evidence_summary: Mapped[str | None]  = mapped_column(Text, nullable=True)
    reviewer_notes: Mapped[str | None]    = mapped_column(Text, nullable=True)
    overdose_risk: Mapped[str | None]     = mapped_column(Text, nullable=True)

    # ── Evidence: JSON arrays (stored as TEXT) ────────────────────────────────
    # Serialise with json.dumps / json.loads in the repository layer.
    # Column name convention: snake_case matching the EvidenceBasedPlant field.
    local_names: Mapped[str | None]                    = mapped_column(Text, nullable=True)
    traditional_systems: Mapped[str | None]            = mapped_column(Text, nullable=True)
    regulatory_status: Mapped[str | None]              = mapped_column(Text, nullable=True)
    therapeutic_claims: Mapped[str | None]             = mapped_column(Text, nullable=True)
    drug_interactions: Mapped[str | None]              = mapped_column(Text, nullable=True)
    safety_warnings: Mapped[str | None]                = mapped_column(Text, nullable=True)
    active_compounds: Mapped[str | None]               = mapped_column(Text, nullable=True)
    dosage_info: Mapped[str | None]                    = mapped_column(Text, nullable=True)
    preparation_methods_structured: Mapped[str | None] = mapped_column(Text, nullable=True)
    citation_flags: Mapped[str | None]                 = mapped_column(Text, nullable=True)
    flagged_issues: Mapped[str | None]                 = mapped_column(Text, nullable=True)

    # ── Evidence: boolean flags (stored as INTEGER 0/1 in SQLite) ────────────
    who_monograph_available: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    ayush_monograph_available: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    detection_results: Mapped[list["DetectionResult"]] = relationship(  # noqa: F821
        "DetectionResult", back_populates="plant"
    )

    def __repr__(self) -> str:
        return f"<Plant(id={self.id}, scientific_name='{self.scientific_name}')>"
