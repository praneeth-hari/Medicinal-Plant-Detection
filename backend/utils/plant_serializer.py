"""
Plant Serializer
================
Bidirectional conversion between EvidenceBasedPlant (Pydantic) and
the Plant ORM model's flat column layout.

Two public functions
--------------------
evidence_to_db_fields(plant)
    Converts an EvidenceBasedPlant into a dict of DB column values.
    - Serialises list/object fields to JSON strings.
    - Derives legacy flat-text fields (medicinal_uses, precautions,
      preparation_methods) so the existing frontend keeps working.

db_to_evidence_plant(orm_plant)
    Reconstructs an EvidenceBasedPlant from an ORM Plant instance.
    Returns None when the plant has no evidence data yet (i.e., all
    new columns are NULL — e.g., plants not yet in the pilot set).
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from models.plant import Plant

logger = logging.getLogger(__name__)

# ── JSON columns — field names that map 1-to-1 between Pydantic and DB ────────
_JSON_FIELDS: list[str] = [
    "local_names",
    "traditional_systems",
    "regulatory_status",
    "therapeutic_claims",
    "drug_interactions",
    "safety_warnings",
    "active_compounds",
    "dosage_info",
    "preparation_methods_structured",
    "citation_flags",
    "flagged_issues",
]

# ── Plain-text columns — field names that map directly ───────────────────────
_TEXT_FIELDS: list[str] = [
    "native_region",
    "last_reviewed",
    "traditional_uses",
    "evidence_summary",
    "reviewer_notes",
    "overdose_risk",
]


def _serialize(value: Any) -> Optional[str]:
    """Serialize a list or object to a compact JSON string, or None."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _deserialize(text: Optional[str]) -> Any:
    """Deserialize a JSON string back to a Python object, or return None."""
    if not text:
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to deserialize JSON column value: %r", text[:80])
        return None


# ── Pydantic → DB ─────────────────────────────────────────────────────────────

def evidence_to_db_fields(evidence_plant) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    """
    Convert an EvidenceBasedPlant into a flat dict of ORM column values.

    Includes:
    - All new evidence columns (indexed, text, JSON, booleans)
    - Derived legacy columns (medicinal_uses, precautions,
      preparation_methods) so the existing frontend renders correctly

    Args:
        evidence_plant: A validated EvidenceBasedPlant instance.

    Returns:
        Dict mapping column name → value, ready to pass to ORM setattr loop.
    """
    from schemas.evidence_schema import EvidenceBasedPlant
    p: EvidenceBasedPlant = evidence_plant

    fields: dict[str, Any] = {}

    # ── Computed indexed columns ──────────────────────────────────────────────
    fields["evidence_strength"] = p.overall_evidence_strength.value
    fields["safety_class"]      = p.safety_class.value
    fields["review_status"]     = p.review_status.value

    # ── Plain text ────────────────────────────────────────────────────────────
    for name in _TEXT_FIELDS:
        fields[name] = getattr(p, name, None)

    # ── JSON arrays/objects ───────────────────────────────────────────────────
    fields["local_names"]           = _serialize(p.local_names)
    fields["traditional_systems"]   = _serialize(p.traditional_systems)
    fields["regulatory_status"]     = _serialize(p.regulatory_status)
    fields["therapeutic_claims"]    = _serialize(
        [c.model_dump() for c in p.therapeutic_claims]
    )
    fields["drug_interactions"]     = _serialize(
        [d.model_dump() for d in p.drug_interactions]
    )
    fields["safety_warnings"]       = _serialize(
        [w.model_dump() for w in p.safety_warnings]
    )
    fields["active_compounds"]      = _serialize(
        [a.model_dump() for a in p.active_compounds]
    )
    fields["dosage_info"]           = _serialize(
        [d.model_dump() for d in p.dosage_info]
    )
    fields["preparation_methods_structured"] = _serialize(
        [m.model_dump() for m in p.preparation_methods]
    )
    fields["citation_flags"]   = _serialize(p.claims_requiring_citation)
    fields["flagged_issues"]   = _serialize(p.flagged_issues)

    # ── Booleans ──────────────────────────────────────────────────────────────
    fields["who_monograph_available"]   = int(p.who_monograph_available)
    fields["ayush_monograph_available"] = int(p.ayush_monograph_available)

    # ── Derived legacy fields (keeps existing frontend working) ───────────────
    fields["medicinal_uses"]       = _derive_medicinal_uses(p)
    fields["precautions"]          = _derive_precautions(p)
    fields["preparation_methods"]  = _derive_preparation_methods(p)

    # Core identity (safe to overwrite — same values)
    fields["common_name"]     = p.common_name
    fields["scientific_name"] = p.scientific_name
    fields["family"]          = p.family
    fields["description"]     = p.description
    fields["habitat"]         = p.habitat

    return fields


# ── DB → Pydantic ─────────────────────────────────────────────────────────────

def db_to_evidence_plant(orm_plant: Plant):  # type: ignore[no-untyped-def]
    """
    Reconstruct an EvidenceBasedPlant from an ORM Plant row.

    Returns None if the plant has no evidence data yet (evidence_strength
    column is NULL, meaning it hasn't been through the pilot conversion).

    Args:
        orm_plant: A Plant ORM instance loaded from the database.

    Returns:
        EvidenceBasedPlant or None.
    """
    if orm_plant.evidence_strength is None:
        return None

    from schemas.evidence_schema import (
        EvidenceBasedPlant,
        TherapeuticClaim,
        DrugInteraction,
        SafetyWarning,
        ActiveCompound,
        DosageInfo,
        PreparationMethod,
    )

    def _parse_list(text: Optional[str], model_cls):
        raw = _deserialize(text)
        if not raw:
            return []
        try:
            return [model_cls(**item) for item in raw]
        except Exception:
            logger.warning("Failed to parse %s from JSON", model_cls.__name__)
            return []

    try:
        return EvidenceBasedPlant(
            common_name=orm_plant.common_name,
            local_names=_deserialize(orm_plant.local_names) or [],
            scientific_name=orm_plant.scientific_name,
            family=orm_plant.family or "",
            description=orm_plant.description or "",
            native_region=orm_plant.native_region or "",
            habitat=orm_plant.habitat or "",
            cultivation_status="Both",   # not stored separately; default
            traditional_systems=_deserialize(orm_plant.traditional_systems) or [],
            traditional_uses_summary=orm_plant.traditional_uses or "",
            therapeutic_claims=_parse_list(orm_plant.therapeutic_claims, TherapeuticClaim),
            evidence_summary=orm_plant.evidence_summary or "",
            preparation_methods=_parse_list(
                orm_plant.preparation_methods_structured, PreparationMethod
            ),
            dosage_info=_parse_list(orm_plant.dosage_info, DosageInfo),
            safety_warnings=_parse_list(orm_plant.safety_warnings, SafetyWarning),
            drug_interactions=_parse_list(orm_plant.drug_interactions, DrugInteraction),
            overdose_risk=orm_plant.overdose_risk,
            active_compounds=_parse_list(orm_plant.active_compounds, ActiveCompound),
            regulatory_status=_deserialize(orm_plant.regulatory_status) or [],
            last_reviewed=orm_plant.last_reviewed,
            claims_requiring_citation=_deserialize(orm_plant.citation_flags) or [],
            flagged_issues=_deserialize(orm_plant.flagged_issues) or [],
            reviewer_notes=orm_plant.reviewer_notes,
            who_monograph_available=bool(orm_plant.who_monograph_available),
            ayush_monograph_available=bool(orm_plant.ayush_monograph_available),
        )
    except Exception:
        logger.exception(
            "Failed to reconstruct EvidenceBasedPlant for '%s'", orm_plant.common_name
        )
        return None


# ── Legacy derivation helpers ─────────────────────────────────────────────────

def _derive_medicinal_uses(p) -> str:  # type: ignore[no-untyped-def]
    """
    Build a flat medicinal_uses text from therapeutic_claims.
    Groups claims by evidence level for readability.
    Used to keep the existing frontend working during the pilot phase.
    """
    if not p.therapeutic_claims:
        return p.traditional_uses_summary or ""

    lines: list[str] = []
    for claim in p.therapeutic_claims:
        lines.append(
            f"• {claim.condition} ({claim.evidence_level.value}): {claim.claim_text}"
        )
    return "\n".join(lines)


def _derive_precautions(p) -> str:  # type: ignore[no-untyped-def]
    """
    Build a flat precautions text from safety_warnings + drug_interactions.
    Prefixes each line with its warning type.
    """
    lines: list[str] = []

    for w in p.safety_warnings:
        lines.append(f"[{w.warning_type}] {w.population}: {w.description}")

    for di in p.drug_interactions:
        lines.append(
            f"[Drug Interaction — {di.severity}] {di.drug_name} "
            f"({di.drug_class}): {di.interaction_description}"
        )

    if p.overdose_risk:
        lines.append(f"[Overdose Risk] {p.overdose_risk}")

    return "\n".join(lines) if lines else "No known precautions documented."


def _derive_preparation_methods(p) -> str:  # type: ignore[no-untyped-def]
    """Build flat preparation_methods text from structured PreparationMethod list."""
    if not p.preparation_methods:
        return ""
    lines: list[str] = []
    for m in p.preparation_methods:
        line = f"• {m.method_name} ({m.plant_part_used}): {m.description}"
        if m.safety_note:
            line += f" — Note: {m.safety_note}"
        lines.append(line)
    return "\n".join(lines)
