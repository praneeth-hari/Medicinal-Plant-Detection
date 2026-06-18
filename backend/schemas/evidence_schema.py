"""
Evidence-Based Medicinal Plant Schema  —  Production-Finalised
================================================================
Design principles:
  - Every therapeutic claim carries its evidence level and study quality.
  - Traditional use is structurally separated from clinical evidence.
  - Safety information distinguishes Contraindication / Precaution / Advisory /
    Monitoring Required at the type level.
  - overall_evidence_strength, safety_class, and review_status are computed
    automatically from source data — never set manually.
  - All citation tracking uses list[str] PMIDs, not single strings.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ── Evidence & quality enums ──────────────────────────────────────────────────

class EvidenceLevel(str, Enum):
    """
    What TYPE of evidence exists for a claim.
    Based on Oxford CEBM levels, adapted for herbal medicine.
    """
    STRONG_CLINICAL   = "Strong Clinical Evidence"    # Multiple RCTs / meta-analyses
    MODERATE_CLINICAL = "Moderate Clinical Evidence"  # At least one RCT
    LIMITED_CLINICAL  = "Limited Clinical Evidence"   # Small trials, pilot studies
    TRADITIONAL_USE   = "Traditional Use Supported"   # Ethnobotanical record only
    PRECLINICAL_ONLY  = "Preclinical Evidence Only"   # Animal / in-vitro only
    INSUFFICIENT      = "Insufficient Evidence"       # Conflicting or no data
    NOT_SUPPORTED     = "Not Scientifically Supported"


class StudyQuality(str, Enum):
    """
    How TRUSTWORTHY is the evidence?
    Separate axis from EvidenceLevel.
    Based on GRADE methodology.
    """
    HIGH     = "High"      # RCT, low bias, adequate power, pre-registered
    MODERATE = "Moderate"  # RCT with limitations, or large well-designed observational
    LOW      = "Low"       # Small trial, high bias risk, uncontrolled
    UNKNOWN  = "Unknown"   # Not assessable from available data


class SafetyClass(str, Enum):
    """Overall safety classification — COMPUTED from safety_warnings."""
    GENERALLY_SAFE    = "Generally Safe"
    USE_WITH_CAUTION  = "Use With Caution"
    PRESCRIPTION_ONLY = "Consult Physician"
    CONTRAINDICATED   = "Contraindicated in Groups"
    INSUFFICIENT_DATA = "Insufficient Safety Data"


class ReviewStatus(str, Enum):
    """Editorial review status — COMPUTED from flagged_issues and citation state."""
    REVIEWED = "Reviewed"
    PENDING  = "Pending Review"
    FLAGGED  = "Flagged"


class InteractionMechanism(str, Enum):
    """Structured mechanism classification for drug interactions."""
    PHARMACOKINETIC_CYP   = "CYP enzyme inhibition/induction"
    PHARMACOKINETIC_TRANS = "Transporter-mediated (P-gp, OATP)"
    PHARMACOKINETIC_OTHER = "Other pharmacokinetic"
    PHARMACODYNAMIC_ADD   = "Additive pharmacodynamic effect"
    PHARMACODYNAMIC_ANT   = "Antagonistic pharmacodynamic effect"
    PROTEIN_BINDING       = "Plasma protein binding displacement"
    UNKNOWN               = "Mechanism unknown"
    NOT_APPLICABLE        = "Not applicable"


# Evidence rank used by the computed overall_evidence_strength
_EVIDENCE_RANK: dict[EvidenceLevel, int] = {
    EvidenceLevel.STRONG_CLINICAL:   6,
    EvidenceLevel.MODERATE_CLINICAL: 5,
    EvidenceLevel.LIMITED_CLINICAL:  4,
    EvidenceLevel.TRADITIONAL_USE:   3,
    EvidenceLevel.PRECLINICAL_ONLY:  2,
    EvidenceLevel.INSUFFICIENT:      1,
    EvidenceLevel.NOT_SUPPORTED:     0,
}


# ── Sub-models ────────────────────────────────────────────────────────────────

class TherapeuticClaim(BaseModel):
    """
    A single evidence-qualified therapeutic claim.
    Every claim must have both an EvidenceLevel (type) and StudyQuality (trustworthiness).
    """
    condition:            str
    claim_text:           str            # Must use evidence-qualified language
    evidence_level:       EvidenceLevel
    study_quality:        StudyQuality   = StudyQuality.UNKNOWN
    source_type:          str            # "RCT", "Meta-Analysis", "Animal Study", etc.
    citation_pmids:       list[str]      = Field(default_factory=list)
    citation_required:    bool           = True
    citation_flag_reason: Optional[str]  = None  # Why no PMID yet


class DrugInteraction(BaseModel):
    """
    A documented or suspected herb-drug interaction with structured mechanism.
    """
    drug_name:               str
    drug_class:              str
    interaction_description: str
    interaction_mechanism:   InteractionMechanism = InteractionMechanism.UNKNOWN
    severity:                str   # "Contraindicated"|"Major"|"Moderate"|"Minor"|"Theoretical"
    evidence_level:          EvidenceLevel
    citation_required:       bool      = True
    citation_pmids:          list[str] = Field(default_factory=list)


class SafetyWarning(BaseModel):
    """
    A typed safety warning for a specific population.
    warning_type drives both display and computed SafetyClass.
    """
    population:        str   # "Pregnant women", "Infants", "Hepatic impairment", etc.
    warning_type:      str   # "Contraindication"|"Precaution"|"Advisory"|"Monitoring Required"
    description:       str
    evidence_level:    EvidenceLevel
    citation_required: bool      = True
    citation_pmids:    list[str] = Field(default_factory=list)


class ActiveCompound(BaseModel):
    """A pharmacologically significant phytochemical."""
    compound_name:    str
    compound_class:   str   # "Terpenoid", "Flavonoid", "Alkaloid", "Polyphenol", etc.
    primary_activity: str
    evidence_level:   EvidenceLevel


class PreparationMethod(BaseModel):
    """How the plant is prepared — process and plant part."""
    method_name:     str
    description:     str
    plant_part_used: str
    intended_use:    str
    safety_note:     Optional[str] = None


class DosageInfo(BaseModel):
    """
    Dosage information — structurally separate from PreparationMethod.
    PreparationMethod answers: how is this prepared?
    DosageInfo answers:        how much, how often, for whom, in which form?
    """
    preparation_form:       str            # "Powder", "Standardised extract", "Tea/Decoction",
                                           # "Fresh juice", "Capsule", "Oil (topical)", "Tincture"
    plant_part:             str            # "Root", "Leaf", "Seed", "Bark", "Aerial parts"
    route:                  str            # "Oral", "Topical", "Inhalation"
    population:             str            # "Adults", "Children 6-12", "Elderly", "General"
    dose_range_min:         Optional[float] = None
    dose_range_max:         Optional[float] = None
    dose_unit:              Optional[str]   = None   # "mg", "g", "ml", "drops"
    frequency:              str             = "Not established"
    max_duration:           Optional[str]   = None   # "12 weeks", "Long-term data insufficient"
    is_clinical_trial_dose: bool            = False  # Was this dose used in an RCT?
    evidence_source:        str             = "Traditional"  # "Clinical trial"|"Traditional"|"Manufacturer"
    citation_pmids:         list[str]       = Field(default_factory=list)
    notes:                  Optional[str]   = None


# ── Master plant model ────────────────────────────────────────────────────────

class EvidenceBasedPlant(BaseModel):
    """
    Production-ready evidence-based medicinal plant record.

    Three fields are COMPUTED automatically and must not be set manually:
      - overall_evidence_strength  (max EvidenceLevel across therapeutic_claims)
      - safety_class               (derived from safety_warnings + drug_interactions)
      - review_status              (derived from flagged_issues + citation state)

    The model_validator always overwrites these, so any manually supplied value
    will be silently replaced.
    """

    # ── Botanical identity ────────────────────────────────────────────────────
    common_name:     str
    local_names:     list[str] = Field(default_factory=list)
    scientific_name: str
    family:          str
    description:     str   # Neutral botanical/cultural description. No efficacy claims.

    # ── Geography ─────────────────────────────────────────────────────────────
    native_region:      str
    habitat:            str
    cultivation_status: str   # "Wild" | "Cultivated" | "Both"

    # ── Phytochemistry ────────────────────────────────────────────────────────
    active_compounds: list[ActiveCompound] = Field(default_factory=list)

    # ── Traditional use (structurally separate from clinical evidence) ─────────
    traditional_systems:      list[str]   # e.g. ["Ayurveda", "Siddha", "Unani"]
    traditional_uses_summary: str         # Must not contain clinical outcome claims

    # ── Therapeutic claims ────────────────────────────────────────────────────
    therapeutic_claims: list[TherapeuticClaim] = Field(default_factory=list)

    # ── Evidence narrative ────────────────────────────────────────────────────
    evidence_summary: str   # One paragraph; describes state of clinical evidence

    # ── Preparation & dosage ──────────────────────────────────────────────────
    preparation_methods: list[PreparationMethod] = Field(default_factory=list)
    dosage_info:         list[DosageInfo]         = Field(default_factory=list)

    # ── Safety ────────────────────────────────────────────────────────────────
    safety_warnings:   list[SafetyWarning]   = Field(default_factory=list)
    drug_interactions: list[DrugInteraction] = Field(default_factory=list)
    overdose_risk:     Optional[str]         = None

    # ── Regulatory ────────────────────────────────────────────────────────────
    regulatory_status: list[str] = Field(default_factory=list)
    # Examples: "AYUSH Monograph", "WHO Monograph", "EMA Herbal Monograph", "FDA GRAS"

    # ── Review metadata ───────────────────────────────────────────────────────
    last_reviewed:             Optional[str] = None   # ISO-8601 "YYYY-MM-DD"
    claims_requiring_citation: list[str]     = Field(default_factory=list)
    flagged_issues:            list[str]     = Field(default_factory=list)
    reviewer_notes:            Optional[str] = None
    who_monograph_available:   bool          = False
    ayush_monograph_available: bool          = False

    # ── COMPUTED FIELDS — do not set manually ─────────────────────────────────
    # model_validator always overwrites these on instantiation.
    overall_evidence_strength: EvidenceLevel = Field(default=EvidenceLevel.INSUFFICIENT)
    safety_class:              SafetyClass   = Field(default=SafetyClass.INSUFFICIENT_DATA)
    review_status:             ReviewStatus  = Field(default=ReviewStatus.PENDING)

    @model_validator(mode='after')
    def _compute_derived_fields(self) -> 'EvidenceBasedPlant':
        self.overall_evidence_strength = self._derive_evidence_strength()
        self.safety_class              = self._derive_safety_class()
        self.review_status             = self._derive_review_status()
        return self

    # ── Derivation logic ──────────────────────────────────────────────────────

    def _derive_evidence_strength(self) -> EvidenceLevel:
        ranked = [
            c for c in self.therapeutic_claims
            if c.evidence_level != EvidenceLevel.NOT_SUPPORTED
        ]
        if not ranked:
            return EvidenceLevel.INSUFFICIENT
        return max(ranked, key=lambda c: _EVIDENCE_RANK[c.evidence_level]).evidence_level

    def _derive_safety_class(self) -> SafetyClass:
        # Contraindication in any warning → CONTRAINDICATED (highest priority)
        for w in self.safety_warnings:
            if w.warning_type == "Contraindication":
                return SafetyClass.CONTRAINDICATED

        # Serious drug interaction → Consult Physician
        for di in self.drug_interactions:
            if di.severity in {"Contraindicated", "Major"}:
                return SafetyClass.PRESCRIPTION_ONLY

        # Any precaution, monitoring, or advisory → Use With Caution
        caution_types = {"Precaution", "Monitoring Required", "Advisory"}
        if any(w.warning_type in caution_types for w in self.safety_warnings):
            return SafetyClass.USE_WITH_CAUTION

        # Minor drug interactions only → Use With Caution
        if self.drug_interactions:
            return SafetyClass.USE_WITH_CAUTION

        if self.safety_warnings or self.drug_interactions:
            return SafetyClass.USE_WITH_CAUTION

        return SafetyClass.GENERALLY_SAFE

    def _derive_review_status(self) -> ReviewStatus:
        # Any editorial flag → FLAGGED
        if self.flagged_issues:
            return ReviewStatus.FLAGGED

        # Any citation_required item with no PMIDs → PENDING
        all_citable: list = (
            list(self.therapeutic_claims)
            + list(self.drug_interactions)
            + list(self.safety_warnings)
        )
        for item in all_citable:
            if getattr(item, 'citation_required', False) and not getattr(item, 'citation_pmids', []):
                return ReviewStatus.PENDING

        return ReviewStatus.REVIEWED


# ── Review constants ──────────────────────────────────────────────────────────

REVIEW_CHECKLIST: list[str] = [
    "R-01  Scientific name is set and non-empty",
    "R-02  Every therapeutic claim has an EvidenceLevel assigned",
    "R-03  No text field contains a BANNED_PHRASE",
    "R-04  PRECLINICAL_ONLY claims contain no human outcome language",
    "R-05  Every Contraindication warning has a PMID or citation_required=False",
    "R-06  Pregnancy safety is explicitly addressed in safety_warnings",
    "R-07  DosageInfo entries with is_clinical_trial_dose=True have citation_pmids",
    "R-08  Infant/paediatric safety is addressed in safety_warnings",
    "R-09  Drug interactions with severity Major/Contraindicated have PMIDs",
    "R-10  All citation_required items have either a PMID or citation_flag_reason",
    "R-11  traditional_uses_summary contains no clinical outcome language",
    "R-12  STRONG_CLINICAL and MODERATE_CLINICAL claims have study_quality != UNKNOWN",
    "R-13  last_reviewed is set and not older than 2 years",
    "R-14  active_compounds list is not empty",
    "R-15  dosage_info list is not empty",
]

BANNED_PHRASES: list[str] = [
    "highly effective", "very effective", "extremely effective",
    "powerful cure", "powerful remedy", "miracle herb",
    "blood purification", "blood cleansing", "detoxification",
    "boosts immunity", "immune booster", "strengthens immunity",
    "guaranteed", "proven to cure", "eliminates cancer",
    "best treatment for", "ideal for treating",
    "no side effects", "completely safe", "100% safe",
    "highly beneficial", "extremely beneficial",
]
