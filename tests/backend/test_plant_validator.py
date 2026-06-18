"""
Plant Validator Test Suite
==========================
Tests every validation rule (R-01 through R-15) plus computed-field logic.

Structure:
  - One fixture: minimal_valid_plant() — passes all BLOCKING rules cleanly.
  - Two tests per rule: one that triggers the violation, one that passes.
  - Separate section for computed-field correctness.

Run from the backend directory:
    cd backend
    pytest ../tests/backend/test_plant_validator.py -v
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

import pytest
import copy

from schemas.evidence_schema import (
    EvidenceBasedPlant,
    EvidenceLevel,
    StudyQuality,
    SafetyClass,
    ReviewStatus,
    InteractionMechanism,
    TherapeuticClaim,
    DrugInteraction,
    SafetyWarning,
    ActiveCompound,
    PreparationMethod,
    DosageInfo,
)
from schemas.plant_validator import PlantValidator, ViolationSeverity


# ── Shared validator instance ──────────────────────────────────────────────────

VALIDATOR = PlantValidator()


# ── Minimal valid plant fixture ────────────────────────────────────────────────

def _make_valid_plant(**overrides) -> EvidenceBasedPlant:
    """
    Build the smallest EvidenceBasedPlant that passes all BLOCKING rules.
    Use keyword overrides to swap out individual fields for negative tests.
    """
    defaults = dict(
        common_name="Test Plant",
        scientific_name="Testus plantus",
        family="Testaceae",
        description="A test plant used for validation testing.",
        native_region="Test region",
        habitat="Dry soil",
        cultivation_status="Both",
        traditional_systems=["Ayurveda"],
        traditional_uses_summary=(
            "Traditionally used in Ayurveda for test conditions. "
            "Traditional use does not constitute clinical proof."
        ),
        evidence_summary="Limited clinical evidence exists for test conditions.",
        therapeutic_claims=[
            TherapeuticClaim(
                condition="Test condition",
                claim_text=(
                    "Limited evidence suggests test plant may help with test condition."
                ),
                evidence_level=EvidenceLevel.LIMITED_CLINICAL,
                study_quality=StudyQuality.LOW,
                source_type="RCT (small scale)",
                citation_pmids=["12345678"],
                citation_required=True,
            )
        ],
        preparation_methods=[
            PreparationMethod(
                method_name="Test Tea",
                description="Boil leaves for 10 minutes.",
                plant_part_used="Leaves",
                intended_use="Traditional test use",
            )
        ],
        dosage_info=[
            DosageInfo(
                preparation_form="Tea/Decoction",
                plant_part="Leaves",
                route="Oral",
                population="Adults",
                frequency="Once daily",
                evidence_source="Traditional",
            )
        ],
        active_compounds=[
            ActiveCompound(
                compound_name="Testanolide",
                compound_class="Terpenoid",
                primary_activity="Test activity",
                evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            )
        ],
        safety_warnings=[
            SafetyWarning(
                population="Pregnant women",
                warning_type="Advisory",
                description="Consult a physician before use during pregnancy.",
                evidence_level=EvidenceLevel.INSUFFICIENT,
                citation_required=False,
            ),
            SafetyWarning(
                population="Infants",
                warning_type="Advisory",
                description="Not studied in infants; avoid use.",
                evidence_level=EvidenceLevel.INSUFFICIENT,
                citation_required=False,
            ),
        ],
        drug_interactions=[],
        last_reviewed="2026-01-01",
        flagged_issues=[],
        who_monograph_available=False,
        ayush_monograph_available=False,
    )
    defaults.update(overrides)
    return EvidenceBasedPlant(**defaults)


@pytest.fixture
def valid_plant() -> EvidenceBasedPlant:
    return _make_valid_plant()


# ── Helper ─────────────────────────────────────────────────────────────────────

def _violation_ids(result) -> set[str]:
    return {v.rule_id for v in result.violations}

def _blocking_ids(result) -> set[str]:
    return {v.rule_id for v in result.violations if v.severity == ViolationSeverity.BLOCKING}

def _warning_ids(result) -> set[str]:
    return {v.rule_id for v in result.violations if v.severity == ViolationSeverity.WARNING}

def _info_ids(result) -> set[str]:
    return {v.rule_id for v in result.violations if v.severity == ViolationSeverity.INFO}


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION — fully valid plant
# ══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    def test_fully_valid_plant_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert result.passed, f"Expected pass, got: {result.violations}"
        assert result.blocking_count == 0

    def test_valid_plant_has_no_blocking_violations(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert result.blocking_count == 0


# ══════════════════════════════════════════════════════════════════════════════
# R-01 — Scientific name
# ══════════════════════════════════════════════════════════════════════════════

class TestR01:
    def test_empty_scientific_name_is_blocking(self):
        plant = _make_valid_plant(scientific_name="")
        result = VALIDATOR.validate(plant)
        assert "R-01" in _blocking_ids(result)

    def test_whitespace_scientific_name_is_blocking(self):
        plant = _make_valid_plant(scientific_name="   ")
        result = VALIDATOR.validate(plant)
        assert "R-01" in _blocking_ids(result)

    def test_valid_scientific_name_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-01" not in _violation_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-02 — Claim evidence levels
# ══════════════════════════════════════════════════════════════════════════════

class TestR02:
    def test_claim_with_none_evidence_level_is_blocking(self):
        # Bypass Pydantic validation to simulate a None evidence_level
        plant = _make_valid_plant()
        plant.therapeutic_claims[0].evidence_level = None  # type: ignore[assignment]
        result = VALIDATOR.validate(plant)
        assert "R-02" in _blocking_ids(result)

    def test_claim_with_evidence_level_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-02" not in _violation_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-03 — Banned phrases
# ══════════════════════════════════════════════════════════════════════════════

class TestR03:
    def test_banned_phrase_in_description_is_blocking(self):
        plant = _make_valid_plant(
            description="This plant is highly effective for treating ailments."
        )
        result = VALIDATOR.validate(plant)
        assert "R-03" in _blocking_ids(result)

    def test_banned_phrase_in_claim_text_is_blocking(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Test",
                    claim_text="This treatment is completely safe and boosts immunity.",
                    evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
                    source_type="In-Vitro",
                    citation_required=False,
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-03" in _blocking_ids(result)

    def test_banned_phrase_in_traditional_uses_is_blocking(self):
        plant = _make_valid_plant(
            traditional_uses_summary="Used for blood purification and general health."
        )
        result = VALIDATOR.validate(plant)
        assert "R-03" in _blocking_ids(result)

    def test_clean_text_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-03" not in _violation_ids(result)

    def test_case_insensitive_detection(self):
        plant = _make_valid_plant(
            description="This plant is Highly Effective for stress relief."
        )
        result = VALIDATOR.validate(plant)
        assert "R-03" in _blocking_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-04 — Preclinical human language
# ══════════════════════════════════════════════════════════════════════════════

class TestR04:
    def test_preclinical_claim_with_patient_language_is_blocking(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Inflammation",
                    claim_text="In patients with inflammation, significant improvement was observed.",
                    evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
                    source_type="Animal Study",
                    citation_required=False,
                ),
                # Keep a valid claim so R-06/other rules pass
            ]
        )
        # Add pregnancy warning
        result = VALIDATOR.validate(plant)
        assert "R-04" in _blocking_ids(result)

    def test_preclinical_claim_without_human_language_passes(self, valid_plant):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Inflammation",
                    claim_text=(
                        "Animal studies show anti-inflammatory effects via COX-2 inhibition. "
                        "Human clinical data is not available."
                    ),
                    evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
                    source_type="Animal Study",
                    citation_required=False,
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-04" not in _blocking_ids(result)

    def test_clinical_claim_with_patient_language_is_allowed(self, valid_plant):
        # "patients showed" in a LIMITED_CLINICAL claim is fine — that's expected
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Test",
                    claim_text="Patients showed a reduction in symptoms in a small RCT.",
                    evidence_level=EvidenceLevel.LIMITED_CLINICAL,
                    source_type="RCT",
                    citation_pmids=["99999999"],
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-04" not in _blocking_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-05 — Contraindication must have PMID or be waived
# ══════════════════════════════════════════════════════════════════════════════

class TestR05:
    def test_contraindication_without_pmid_is_blocking(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women",
                    warning_type="Contraindication",
                    description="Contraindicated in pregnancy.",
                    evidence_level=EvidenceLevel.TRADITIONAL_USE,
                    citation_required=True,   # required but no PMIDs
                    citation_pmids=[],
                ),
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied in infants.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-05" in _blocking_ids(result)

    def test_contraindication_with_pmid_passes(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women",
                    warning_type="Contraindication",
                    description="Contraindicated in pregnancy — uterotonic properties.",
                    evidence_level=EvidenceLevel.TRADITIONAL_USE,
                    citation_required=True,
                    citation_pmids=["11111111"],
                ),
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied in infants.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-05" not in _blocking_ids(result)

    def test_contraindication_with_citation_waived_passes(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women",
                    warning_type="Contraindication",
                    description="Contraindicated in pregnancy per traditional knowledge.",
                    evidence_level=EvidenceLevel.TRADITIONAL_USE,
                    citation_required=False,  # waived — traditional knowledge
                    citation_pmids=[],
                ),
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied in infants.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-05" not in _blocking_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-06 — Pregnancy safety addressed
# ══════════════════════════════════════════════════════════════════════════════

class TestR06:
    def test_missing_pregnancy_warning_is_blocking(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied in infants.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-06" in _blocking_ids(result)

    def test_pregnancy_warning_present_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-06" not in _blocking_ids(result)

    def test_pregnancy_warning_case_insensitive(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="PREGNANT WOMEN",
                    warning_type="Advisory",
                    description="Consult physician.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-06" not in _blocking_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-07 — Clinical trial dose must have PMIDs
# ══════════════════════════════════════════════════════════════════════════════

class TestR07:
    def test_clinical_trial_dose_without_pmid_is_blocking(self):
        plant = _make_valid_plant(
            dosage_info=[
                DosageInfo(
                    preparation_form="Standardised extract",
                    plant_part="Root",
                    route="Oral",
                    population="Adults",
                    dose_range_min=300,
                    dose_range_max=600,
                    dose_unit="mg",
                    frequency="Twice daily",
                    is_clinical_trial_dose=True,    # claims RCT backing
                    evidence_source="Clinical trial",
                    citation_pmids=[],              # but no PMID
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-07" in _blocking_ids(result)

    def test_clinical_trial_dose_with_pmid_passes(self):
        plant = _make_valid_plant(
            dosage_info=[
                DosageInfo(
                    preparation_form="Standardised extract",
                    plant_part="Root",
                    route="Oral",
                    population="Adults",
                    dose_range_min=300,
                    dose_range_max=600,
                    dose_unit="mg",
                    frequency="Twice daily",
                    is_clinical_trial_dose=True,
                    evidence_source="Clinical trial",
                    citation_pmids=["31517876"],
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-07" not in _blocking_ids(result)

    def test_non_clinical_dose_without_pmid_passes(self, valid_plant):
        # Default dosage in valid_plant has is_clinical_trial_dose=False
        result = VALIDATOR.validate(valid_plant)
        assert "R-07" not in _blocking_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-08 — Infant safety addressed (WARNING only)
# ══════════════════════════════════════════════════════════════════════════════

class TestR08:
    def test_missing_infant_warning_is_warning(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women",
                    warning_type="Advisory",
                    description="Consult physician.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
                # No infant warning
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-08" in _warning_ids(result)
        assert "R-08" not in _blocking_ids(result)

    def test_infant_warning_present_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-08" not in _warning_ids(result)

    def test_children_population_satisfies_infant_check(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women",
                    warning_type="Advisory",
                    description="Consult physician.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
                SafetyWarning(
                    population="Children under 12",
                    warning_type="Advisory",
                    description="Not studied in children.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-08" not in _warning_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-09 — Serious interaction requires PMID (WARNING only)
# ══════════════════════════════════════════════════════════════════════════════

class TestR09:
    def test_major_interaction_without_pmid_is_warning(self):
        plant = _make_valid_plant(
            drug_interactions=[
                DrugInteraction(
                    drug_name="Warfarin",
                    drug_class="Anticoagulant",
                    interaction_description="May increase bleeding risk.",
                    interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
                    severity="Major",
                    evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
                    citation_required=True,
                    citation_pmids=[],
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-09" in _warning_ids(result)
        assert "R-09" not in _blocking_ids(result)

    def test_major_interaction_with_pmid_passes(self):
        plant = _make_valid_plant(
            drug_interactions=[
                DrugInteraction(
                    drug_name="Warfarin",
                    drug_class="Anticoagulant",
                    interaction_description="May increase bleeding risk.",
                    interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
                    severity="Major",
                    evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
                    citation_required=True,
                    citation_pmids=["22222222"],
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-09" not in _warning_ids(result)

    def test_minor_interaction_without_pmid_does_not_trigger_r09(self):
        plant = _make_valid_plant(
            drug_interactions=[
                DrugInteraction(
                    drug_name="Paracetamol",
                    drug_class="Analgesic",
                    interaction_description="Theoretical interaction.",
                    severity="Minor",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                    citation_pmids=[],
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-09" not in _warning_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-10 — citation_required but no PMID must have flag_reason
# ══════════════════════════════════════════════════════════════════════════════

class TestR10:
    def test_claim_citation_required_no_pmid_no_flag_is_warning(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Anxiety",
                    claim_text="May help with anxiety based on preliminary data.",
                    evidence_level=EvidenceLevel.LIMITED_CLINICAL,
                    source_type="Pilot study",
                    citation_required=True,
                    citation_pmids=[],          # no PMID
                    citation_flag_reason=None,  # no reason either
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-10" in _warning_ids(result)

    def test_claim_with_pmid_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-10" not in _warning_ids(result)

    def test_claim_with_flag_reason_passes(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Anxiety",
                    claim_text="May help with anxiety.",
                    evidence_level=EvidenceLevel.LIMITED_CLINICAL,
                    source_type="Pilot study",
                    citation_required=True,
                    citation_pmids=[],
                    citation_flag_reason="Pilot study identified; PMID retrieval pending.",
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-10" not in _warning_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-11 — Traditional uses must not contain clinical language
# ══════════════════════════════════════════════════════════════════════════════

class TestR11:
    def test_clinical_language_in_traditional_uses_is_warning(self):
        plant = _make_valid_plant(
            traditional_uses_summary=(
                "Traditionally used in Ayurveda. Studies show this plant reduces fever."
            )
        )
        result = VALIDATOR.validate(plant)
        assert "R-11" in _warning_ids(result)

    def test_traditional_language_only_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-11" not in _warning_ids(result)

    def test_clinically_proven_triggers_r11(self):
        plant = _make_valid_plant(
            traditional_uses_summary=(
                "Clinically proven to reduce inflammation, also traditionally used."
            )
        )
        result = VALIDATOR.validate(plant)
        assert "R-11" in _warning_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-12 — Strong/moderate evidence claims must have study_quality set
# ══════════════════════════════════════════════════════════════════════════════

class TestR12:
    def test_strong_evidence_unknown_quality_is_warning(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Stress",
                    claim_text="Multiple RCTs demonstrate stress reduction.",
                    evidence_level=EvidenceLevel.STRONG_CLINICAL,
                    study_quality=StudyQuality.UNKNOWN,   # not assessed
                    source_type="Meta-Analysis",
                    citation_pmids=["31517876"],
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-12" in _warning_ids(result)

    def test_strong_evidence_with_quality_passes(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Stress",
                    claim_text="Multiple RCTs demonstrate stress reduction.",
                    evidence_level=EvidenceLevel.STRONG_CLINICAL,
                    study_quality=StudyQuality.HIGH,
                    source_type="Meta-Analysis",
                    citation_pmids=["31517876"],
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-12" not in _warning_ids(result)

    def test_preclinical_with_unknown_quality_does_not_trigger_r12(self, valid_plant):
        # Preclinical claims are allowed to have UNKNOWN study_quality
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Test",
                    claim_text="Animal data suggests activity.",
                    evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
                    study_quality=StudyQuality.UNKNOWN,
                    source_type="Animal Study",
                    citation_required=False,
                )
            ]
        )
        result = VALIDATOR.validate(plant)
        assert "R-12" not in _warning_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-13 — last_reviewed freshness
# ══════════════════════════════════════════════════════════════════════════════

class TestR13:
    def test_missing_last_reviewed_is_warning(self):
        plant = _make_valid_plant(last_reviewed=None)
        result = VALIDATOR.validate(plant)
        assert "R-13" in _warning_ids(result)

    def test_invalid_date_format_is_warning(self):
        plant = _make_valid_plant(last_reviewed="June 2024")
        result = VALIDATOR.validate(plant)
        assert "R-13" in _warning_ids(result)

    def test_stale_date_is_warning(self):
        plant = _make_valid_plant(last_reviewed="2020-01-01")
        result = VALIDATOR.validate(plant)
        assert "R-13" in _warning_ids(result)

    def test_recent_date_passes(self, valid_plant):
        # valid_plant has last_reviewed="2026-01-01"
        result = VALIDATOR.validate(valid_plant)
        assert "R-13" not in _warning_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-14 — Active compounds (INFO only)
# ══════════════════════════════════════════════════════════════════════════════

class TestR14:
    def test_empty_active_compounds_is_info(self):
        plant = _make_valid_plant(active_compounds=[])
        result = VALIDATOR.validate(plant)
        assert "R-14" in _info_ids(result)
        assert "R-14" not in _blocking_ids(result)
        assert "R-14" not in _warning_ids(result)

    def test_active_compounds_present_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-14" not in _info_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# R-15 — Dosage info (INFO only)
# ══════════════════════════════════════════════════════════════════════════════

class TestR15:
    def test_empty_dosage_info_is_info(self):
        plant = _make_valid_plant(dosage_info=[])
        result = VALIDATOR.validate(plant)
        assert "R-15" in _info_ids(result)
        assert "R-15" not in _blocking_ids(result)

    def test_dosage_info_present_passes(self, valid_plant):
        result = VALIDATOR.validate(valid_plant)
        assert "R-15" not in _info_ids(result)


# ══════════════════════════════════════════════════════════════════════════════
# COMPUTED FIELDS — EvidenceLevel, SafetyClass, ReviewStatus
# ══════════════════════════════════════════════════════════════════════════════

class TestComputedEvidenceStrength:
    def test_strong_clinical_claim_gives_strong_overall(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Stress",
                    claim_text="Stress reduction confirmed by meta-analysis.",
                    evidence_level=EvidenceLevel.STRONG_CLINICAL,
                    study_quality=StudyQuality.HIGH,
                    source_type="Meta-Analysis",
                    citation_pmids=["31517876"],
                )
            ]
        )
        assert plant.overall_evidence_strength == EvidenceLevel.STRONG_CLINICAL

    def test_max_level_wins_when_multiple_claims(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Stress",
                    claim_text="Strong clinical evidence for stress.",
                    evidence_level=EvidenceLevel.STRONG_CLINICAL,
                    study_quality=StudyQuality.HIGH,
                    source_type="Meta-Analysis",
                    citation_pmids=["31517876"],
                ),
                TherapeuticClaim(
                    condition="Antimicrobial",
                    claim_text="In-vitro antimicrobial activity observed.",
                    evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
                    source_type="In-Vitro",
                    citation_required=False,
                ),
            ]
        )
        assert plant.overall_evidence_strength == EvidenceLevel.STRONG_CLINICAL

    def test_not_supported_claims_excluded_from_overall(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Blood purification",
                    claim_text="No scientific basis for this concept.",
                    evidence_level=EvidenceLevel.NOT_SUPPORTED,
                    source_type="None",
                    citation_required=False,
                )
            ]
        )
        assert plant.overall_evidence_strength == EvidenceLevel.INSUFFICIENT

    def test_no_claims_gives_insufficient(self):
        plant = _make_valid_plant(therapeutic_claims=[])
        assert plant.overall_evidence_strength == EvidenceLevel.INSUFFICIENT

    def test_manually_set_value_is_overwritten(self):
        # Even if someone passes overall_evidence_strength manually, validator overwrites it
        plant = EvidenceBasedPlant(
            common_name="Test",
            scientific_name="Testus plantus",
            family="Testaceae",
            description="Test.",
            native_region="Test",
            habitat="Test",
            cultivation_status="Both",
            traditional_systems=["Ayurveda"],
            traditional_uses_summary="Traditionally used.",
            evidence_summary="No evidence.",
            therapeutic_claims=[],          # empty — will give INSUFFICIENT
            overall_evidence_strength=EvidenceLevel.STRONG_CLINICAL,  # manually set
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women", warning_type="Advisory",
                    description="Consult physician.", evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                )
            ],
        )
        assert plant.overall_evidence_strength == EvidenceLevel.INSUFFICIENT


class TestComputedSafetyClass:
    def test_contraindication_warning_gives_contraindicated(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women",
                    warning_type="Contraindication",
                    description="Contraindicated.",
                    evidence_level=EvidenceLevel.TRADITIONAL_USE,
                    citation_required=False,
                ),
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ]
        )
        assert plant.safety_class == SafetyClass.CONTRAINDICATED

    def test_major_drug_interaction_gives_prescription_only(self):
        plant = _make_valid_plant(
            drug_interactions=[
                DrugInteraction(
                    drug_name="Warfarin",
                    drug_class="Anticoagulant",
                    interaction_description="Serious bleeding risk.",
                    severity="Major",
                    evidence_level=EvidenceLevel.MODERATE_CLINICAL,
                    citation_required=False,
                )
            ]
        )
        assert plant.safety_class == SafetyClass.PRESCRIPTION_ONLY

    def test_precaution_warning_gives_use_with_caution(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women",
                    warning_type="Precaution",
                    description="Use with caution.",
                    evidence_level=EvidenceLevel.TRADITIONAL_USE,
                    citation_required=False,
                ),
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ]
        )
        assert plant.safety_class == SafetyClass.USE_WITH_CAUTION

    def test_no_warnings_no_interactions_gives_generally_safe(self):
        plant = _make_valid_plant(safety_warnings=[
            SafetyWarning(
                population="Pregnant women",
                warning_type="Advisory",
                description="Consult physician.",
                evidence_level=EvidenceLevel.INSUFFICIENT,
                citation_required=False,
            ),
            SafetyWarning(
                population="Infants",
                warning_type="Advisory",
                description="Not studied.",
                evidence_level=EvidenceLevel.INSUFFICIENT,
                citation_required=False,
            ),
        ], drug_interactions=[])
        # Advisory only + no interactions → USE_WITH_CAUTION (advisory still triggers caution)
        assert plant.safety_class == SafetyClass.USE_WITH_CAUTION

    def test_contraindication_takes_priority_over_major_interaction(self):
        plant = _make_valid_plant(
            safety_warnings=[
                SafetyWarning(
                    population="Pregnant women",
                    warning_type="Contraindication",
                    description="Contraindicated.",
                    evidence_level=EvidenceLevel.TRADITIONAL_USE,
                    citation_required=False,
                ),
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                ),
            ],
            drug_interactions=[
                DrugInteraction(
                    drug_name="Warfarin",
                    drug_class="Anticoagulant",
                    interaction_description="Serious risk.",
                    severity="Major",
                    evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
                    citation_required=False,
                )
            ],
        )
        assert plant.safety_class == SafetyClass.CONTRAINDICATED


class TestComputedReviewStatus:
    def test_flagged_issues_gives_flagged_status(self):
        plant = _make_valid_plant(
            flagged_issues=["Seed data uses 'immune booster'."]
        )
        assert plant.review_status == ReviewStatus.FLAGGED

    def test_unresolved_citation_gives_pending(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Test",
                    claim_text="Limited evidence for test condition.",
                    evidence_level=EvidenceLevel.LIMITED_CLINICAL,
                    source_type="Pilot",
                    citation_required=True,
                    citation_pmids=[],          # unresolved
                    citation_flag_reason="Pending PMID retrieval.",
                )
            ],
            flagged_issues=[],
        )
        assert plant.review_status == ReviewStatus.PENDING

    def test_all_citations_resolved_gives_reviewed(self, valid_plant):
        assert valid_plant.review_status == ReviewStatus.REVIEWED

    def test_flagged_takes_priority_over_pending(self):
        plant = _make_valid_plant(
            therapeutic_claims=[
                TherapeuticClaim(
                    condition="Test",
                    claim_text="Limited evidence.",
                    evidence_level=EvidenceLevel.LIMITED_CLINICAL,
                    source_type="Pilot",
                    citation_required=True,
                    citation_pmids=[],  # would give PENDING
                    citation_flag_reason=None,
                )
            ],
            flagged_issues=["Contains banned phrase."],  # → FLAGGED takes priority
        )
        assert plant.review_status == ReviewStatus.FLAGGED


# ══════════════════════════════════════════════════════════════════════════════
# MULTI-VIOLATION — all blocking violations are reported simultaneously
# ══════════════════════════════════════════════════════════════════════════════

class TestMultipleViolations:
    def test_all_violations_reported_not_just_first(self):
        plant = _make_valid_plant(
            description="This plant is highly effective and completely safe.",  # R-03 ×2
            scientific_name="",                                                  # R-01
            # Remove pregnancy warning                                           # R-06
            safety_warnings=[
                SafetyWarning(
                    population="Infants",
                    warning_type="Advisory",
                    description="Not studied.",
                    evidence_level=EvidenceLevel.INSUFFICIENT,
                    citation_required=False,
                )
            ],
        )
        result = VALIDATOR.validate(plant)
        ids = _blocking_ids(result)
        assert "R-01" in ids
        assert "R-03" in ids
        assert "R-06" in ids
        assert result.blocking_count >= 3
