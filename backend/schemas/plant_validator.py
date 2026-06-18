"""
Plant Validator
===============
Validates an EvidenceBasedPlant instance against all 15 review rules.

Severity levels:
  BLOCKING — plant must not be seeded or published until resolved
  WARNING  — should be resolved before production; does not block seeding
  INFO     — informational; does not block seeding

Usage:
    from schemas.plant_validator import PlantValidator
    result = PlantValidator().validate(plant)
    if not result.passed:
        for v in result.blocking_violations:
            print(v)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from schemas.evidence_schema import (
    BANNED_PHRASES,
    EvidenceBasedPlant,
    EvidenceLevel,
    StudyQuality,
)

# ── Violation types ────────────────────────────────────────────────────────────

class ViolationSeverity(str, Enum):
    BLOCKING = "BLOCKING"
    WARNING  = "WARNING"
    INFO     = "INFO"


@dataclass
class Violation:
    severity:   ViolationSeverity
    rule_id:    str    # e.g. "R-03"
    field_path: str    # e.g. "therapeutic_claims[1].claim_text"
    message:    str

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.rule_id}  {self.field_path}: {self.message}"


@dataclass
class ValidationResult:
    plant_name: str
    passed:     bool   # True only when zero BLOCKING violations exist
    violations: list[Violation] = field(default_factory=list)

    @property
    def blocking_violations(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == ViolationSeverity.BLOCKING]

    @property
    def warning_violations(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == ViolationSeverity.WARNING]

    @property
    def info_violations(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == ViolationSeverity.INFO]

    @property
    def blocking_count(self) -> int:
        return len(self.blocking_violations)

    @property
    def warning_count(self) -> int:
        return len(self.warning_violations)

    @property
    def info_count(self) -> int:
        return len(self.info_violations)


# ── Internal signal lists ──────────────────────────────────────────────────────

# R-04: language that implies human outcome inside a PRECLINICAL claim
_PRECLINICAL_HUMAN_SIGNALS: list[str] = [
    "patients showed",
    "patients reported",
    "patients experienced",
    "patients treated",
    "participants reported",
    "participants showed",
    "volunteers showed",
    "study participants",
    "clinical improvement",
    "in patients with",
    "human subjects showed",
]

# R-11: language that implies clinical proof inside traditional_uses_summary
_CLINICAL_LANGUAGE_SIGNALS: list[str] = [
    "clinically proven",
    "clinical trials show",
    "studies show",
    "evidence shows",
    "proven effective",
    "scientifically proven",
    "research confirms",
    "studies confirm",
    "trials demonstrate",
    "has been shown to",
    "is proven to",
    "is clinically",
    "medical studies show",
    "scientific evidence shows",
    "clinical research shows",
]

# R-06: normalised pregnancy population strings
_PREGNANCY_TOKENS: set[str] = {"pregnant women", "pregnancy", "pregnant"}

# R-08: normalised infant/paediatric population strings
_INFANT_TOKENS: set[str] = {
    "infants", "infant", "children", "child",
    "paediatric", "pediatric", "neonates", "newborns", "babies",
}

# R-09: interaction severities that require PMIDs
_SERIOUS_SEVERITIES: set[str] = {"Contraindicated", "Major"}

# R-12: evidence levels that require an assessed study_quality
_QUALITY_REQUIRED_LEVELS: set[EvidenceLevel] = {
    EvidenceLevel.STRONG_CLINICAL,
    EvidenceLevel.MODERATE_CLINICAL,
}

_STALENESS_YEARS: float = 2.0


# ── Validator ─────────────────────────────────────────────────────────────────

class PlantValidator:
    """
    Runs all 15 validation rules against an EvidenceBasedPlant.
    Rules are independent — all are always executed so every violation is visible.
    """

    def validate(self, plant: EvidenceBasedPlant) -> ValidationResult:
        violations: list[Violation] = []
        violations += self._r01_scientific_name(plant)
        violations += self._r02_claim_evidence_levels(plant)
        violations += self._r03_banned_phrases(plant)
        violations += self._r04_preclinical_human_language(plant)
        violations += self._r05_contraindication_pmid_or_waived(plant)
        violations += self._r06_pregnancy_addressed(plant)
        violations += self._r07_clinical_dose_pmid(plant)
        violations += self._r08_infant_addressed(plant)
        violations += self._r09_serious_interaction_pmid(plant)
        violations += self._r10_citation_required_flag_present(plant)
        violations += self._r11_traditional_uses_no_clinical_language(plant)
        violations += self._r12_strong_evidence_study_quality(plant)
        violations += self._r13_last_reviewed_freshness(plant)
        violations += self._r14_active_compounds_present(plant)
        violations += self._r15_dosage_info_present(plant)

        passed = not any(v.severity == ViolationSeverity.BLOCKING for v in violations)
        return ValidationResult(plant_name=plant.common_name, passed=passed, violations=violations)

    # ── Rule R-01 ─────────────────────────────────────────────────────────────

    def _r01_scientific_name(self, plant: EvidenceBasedPlant) -> list[Violation]:
        if not plant.scientific_name or not plant.scientific_name.strip():
            return [Violation(
                severity=ViolationSeverity.BLOCKING,
                rule_id="R-01",
                field_path="scientific_name",
                message="scientific_name is empty.",
            )]
        return []

    # ── Rule R-02 ─────────────────────────────────────────────────────────────

    def _r02_claim_evidence_levels(self, plant: EvidenceBasedPlant) -> list[Violation]:
        out = []
        for i, c in enumerate(plant.therapeutic_claims):
            if c.evidence_level is None:
                out.append(Violation(
                    severity=ViolationSeverity.BLOCKING,
                    rule_id="R-02",
                    field_path=f"therapeutic_claims[{i}].evidence_level",
                    message=f"Claim '{c.condition}' has no evidence_level.",
                ))
        return out

    # ── Rule R-03 ─────────────────────────────────────────────────────────────

    def _r03_banned_phrases(self, plant: EvidenceBasedPlant) -> list[Violation]:
        out: list[Violation] = []

        def _scan(text: str | None, path: str) -> None:
            if not text:
                return
            lower = text.lower()
            for phrase in BANNED_PHRASES:
                if phrase in lower:
                    out.append(Violation(
                        severity=ViolationSeverity.BLOCKING,
                        rule_id="R-03",
                        field_path=path,
                        message=f"Banned phrase detected: '{phrase}'",
                    ))

        _scan(plant.description, "description")
        _scan(plant.traditional_uses_summary, "traditional_uses_summary")
        _scan(plant.evidence_summary, "evidence_summary")

        for i, c in enumerate(plant.therapeutic_claims):
            _scan(c.claim_text, f"therapeutic_claims[{i}].claim_text")

        for i, w in enumerate(plant.safety_warnings):
            _scan(w.description, f"safety_warnings[{i}].description")

        return out

    # ── Rule R-04 ─────────────────────────────────────────────────────────────

    def _r04_preclinical_human_language(self, plant: EvidenceBasedPlant) -> list[Violation]:
        out = []
        for i, c in enumerate(plant.therapeutic_claims):
            if c.evidence_level != EvidenceLevel.PRECLINICAL_ONLY:
                continue
            lower = c.claim_text.lower()
            for signal in _PRECLINICAL_HUMAN_SIGNALS:
                if signal in lower:
                    out.append(Violation(
                        severity=ViolationSeverity.BLOCKING,
                        rule_id="R-04",
                        field_path=f"therapeutic_claims[{i}].claim_text",
                        message=(
                            f"Preclinical-only claim for '{c.condition}' uses human outcome "
                            f"language: '{signal}'. Rewrite to remove implied human evidence."
                        ),
                    ))
                    break  # one violation per claim
        return out

    # ── Rule R-05 ─────────────────────────────────────────────────────────────

    def _r05_contraindication_pmid_or_waived(self, plant: EvidenceBasedPlant) -> list[Violation]:
        out = []
        for i, w in enumerate(plant.safety_warnings):
            if w.warning_type != "Contraindication":
                continue
            if w.citation_required and not w.citation_pmids:
                out.append(Violation(
                    severity=ViolationSeverity.BLOCKING,
                    rule_id="R-05",
                    field_path=f"safety_warnings[{i}]",
                    message=(
                        f"Contraindication for '{w.population}' has no PMID. "
                        "Either add a citation_pmids entry or set citation_required=False."
                    ),
                ))
        return out

    # ── Rule R-06 ─────────────────────────────────────────────────────────────

    def _r06_pregnancy_addressed(self, plant: EvidenceBasedPlant) -> list[Violation]:
        populations = {w.population.lower() for w in plant.safety_warnings}
        if any(
            token in pop
            for pop in populations
            for token in _PREGNANCY_TOKENS
        ):
            return []
        return [Violation(
            severity=ViolationSeverity.BLOCKING,
            rule_id="R-06",
            field_path="safety_warnings",
            message=(
                "Pregnancy safety is not addressed. "
                "Add a SafetyWarning for 'Pregnant women'."
            ),
        )]

    # ── Rule R-07 ─────────────────────────────────────────────────────────────

    def _r07_clinical_dose_pmid(self, plant: EvidenceBasedPlant) -> list[Violation]:
        out = []
        for i, d in enumerate(plant.dosage_info):
            if d.is_clinical_trial_dose and not d.citation_pmids:
                out.append(Violation(
                    severity=ViolationSeverity.BLOCKING,
                    rule_id="R-07",
                    field_path=f"dosage_info[{i}].citation_pmids",
                    message=(
                        f"DosageInfo '{d.preparation_form}' for '{d.population}' is marked "
                        "is_clinical_trial_dose=True but has no citation_pmids."
                    ),
                ))
        return out

    # ── Rule R-08 ─────────────────────────────────────────────────────────────

    def _r08_infant_addressed(self, plant: EvidenceBasedPlant) -> list[Violation]:
        populations = {w.population.lower() for w in plant.safety_warnings}
        if any(
            token in pop
            for pop in populations
            for token in _INFANT_TOKENS
        ):
            return []
        return [Violation(
            severity=ViolationSeverity.WARNING,
            rule_id="R-08",
            field_path="safety_warnings",
            message=(
                "Infant/paediatric safety is not addressed. "
                "Add a SafetyWarning for 'Infants' or 'Children'."
            ),
        )]

    # ── Rule R-09 ─────────────────────────────────────────────────────────────

    def _r09_serious_interaction_pmid(self, plant: EvidenceBasedPlant) -> list[Violation]:
        out = []
        for i, di in enumerate(plant.drug_interactions):
            if di.severity in _SERIOUS_SEVERITIES and not di.citation_pmids:
                out.append(Violation(
                    severity=ViolationSeverity.WARNING,
                    rule_id="R-09",
                    field_path=f"drug_interactions[{i}].citation_pmids",
                    message=(
                        f"Interaction with '{di.drug_name}' (severity='{di.severity}') "
                        "has no supporting PMID."
                    ),
                ))
        return out

    # ── Rule R-10 ─────────────────────────────────────────────────────────────

    def _r10_citation_required_flag_present(self, plant: EvidenceBasedPlant) -> list[Violation]:
        out: list[Violation] = []

        for i, c in enumerate(plant.therapeutic_claims):
            if c.citation_required and not c.citation_pmids and not c.citation_flag_reason:
                out.append(Violation(
                    severity=ViolationSeverity.WARNING,
                    rule_id="R-10",
                    field_path=f"therapeutic_claims[{i}]",
                    message=(
                        f"Claim '{c.condition}' has citation_required=True but no PMID "
                        "and no citation_flag_reason explaining why."
                    ),
                ))

        for i, di in enumerate(plant.drug_interactions):
            if di.citation_required and not di.citation_pmids:
                out.append(Violation(
                    severity=ViolationSeverity.WARNING,
                    rule_id="R-10",
                    field_path=f"drug_interactions[{i}].citation_pmids",
                    message=(
                        f"Drug interaction with '{di.drug_name}' has citation_required=True "
                        "but no PMID."
                    ),
                ))

        for i, w in enumerate(plant.safety_warnings):
            if w.warning_type == "Advisory":
                continue  # Advisory warnings are informational; PMID not mandatory
            if w.citation_required and not w.citation_pmids:
                out.append(Violation(
                    severity=ViolationSeverity.WARNING,
                    rule_id="R-10",
                    field_path=f"safety_warnings[{i}].citation_pmids",
                    message=(
                        f"Safety warning ({w.warning_type}) for '{w.population}' "
                        "has citation_required=True but no PMID."
                    ),
                ))

        return out

    # ── Rule R-11 ─────────────────────────────────────────────────────────────

    def _r11_traditional_uses_no_clinical_language(
        self, plant: EvidenceBasedPlant
    ) -> list[Violation]:
        if not plant.traditional_uses_summary:
            return []
        lower = plant.traditional_uses_summary.lower()
        for signal in _CLINICAL_LANGUAGE_SIGNALS:
            if signal in lower:
                return [Violation(
                    severity=ViolationSeverity.WARNING,
                    rule_id="R-11",
                    field_path="traditional_uses_summary",
                    message=(
                        f"Traditional uses section contains clinical language: '{signal}'. "
                        "This section must only describe traditional/ethnobotanical use — "
                        "not clinical outcomes."
                    ),
                )]
        return []

    # ── Rule R-12 ─────────────────────────────────────────────────────────────

    def _r12_strong_evidence_study_quality(self, plant: EvidenceBasedPlant) -> list[Violation]:
        out = []
        for i, c in enumerate(plant.therapeutic_claims):
            if (
                c.evidence_level in _QUALITY_REQUIRED_LEVELS
                and c.study_quality == StudyQuality.UNKNOWN
            ):
                out.append(Violation(
                    severity=ViolationSeverity.WARNING,
                    rule_id="R-12",
                    field_path=f"therapeutic_claims[{i}].study_quality",
                    message=(
                        f"Claim '{c.condition}' has evidence_level="
                        f"'{c.evidence_level.value}' but study_quality is UNKNOWN. "
                        "Assess and set High, Moderate, or Low."
                    ),
                ))
        return out

    # ── Rule R-13 ─────────────────────────────────────────────────────────────

    def _r13_last_reviewed_freshness(self, plant: EvidenceBasedPlant) -> list[Violation]:
        if not plant.last_reviewed:
            return [Violation(
                severity=ViolationSeverity.WARNING,
                rule_id="R-13",
                field_path="last_reviewed",
                message="last_reviewed date is not set.",
            )]

        try:
            reviewed = date.fromisoformat(plant.last_reviewed)
        except ValueError:
            return [Violation(
                severity=ViolationSeverity.WARNING,
                rule_id="R-13",
                field_path="last_reviewed",
                message=(
                    f"last_reviewed '{plant.last_reviewed}' is not a valid "
                    "ISO-8601 date (expected YYYY-MM-DD)."
                ),
            )]

        years_old = (date.today() - reviewed).days / 365.25
        if years_old > _STALENESS_YEARS:
            return [Violation(
                severity=ViolationSeverity.WARNING,
                rule_id="R-13",
                field_path="last_reviewed",
                message=(
                    f"Plant was last reviewed {plant.last_reviewed} "
                    f"({years_old:.1f} years ago). Evidence review recommended."
                ),
            )]
        return []

    # ── Rule R-14 ─────────────────────────────────────────────────────────────

    def _r14_active_compounds_present(self, plant: EvidenceBasedPlant) -> list[Violation]:
        if not plant.active_compounds:
            return [Violation(
                severity=ViolationSeverity.INFO,
                rule_id="R-14",
                field_path="active_compounds",
                message="No active compounds are documented.",
            )]
        return []

    # ── Rule R-15 ─────────────────────────────────────────────────────────────

    def _r15_dosage_info_present(self, plant: EvidenceBasedPlant) -> list[Violation]:
        if not plant.dosage_info:
            return [Violation(
                severity=ViolationSeverity.INFO,
                rule_id="R-15",
                field_path="dosage_info",
                message="No dosage information is documented.",
            )]
        return []
