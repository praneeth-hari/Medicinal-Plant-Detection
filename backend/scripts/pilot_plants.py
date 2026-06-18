"""
Pilot Plants — Evidence-Based Data
====================================
5 plants fully populated using the finalised EvidenceBasedPlant schema.
All 15 validation rules satisfied; no BLOCKING violations.

Plants: Tulsi, Neem, Ashwagandha, Turmeric, Bael
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.evidence_schema import (
    EvidenceBasedPlant,
    EvidenceLevel,
    StudyQuality,
    InteractionMechanism,
    TherapeuticClaim,
    DrugInteraction,
    SafetyWarning,
    ActiveCompound,
    PreparationMethod,
    DosageInfo,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. TULSI  (Ocimum tenuiflorum)
# ═══════════════════════════════════════════════════════════════════════════════

TULSI = EvidenceBasedPlant(
    common_name="Tulsi",
    local_names=["Holy Basil", "Sacred Basil", "Tulasi", "Vrinda"],
    scientific_name="Ocimum tenuiflorum",
    family="Lamiaceae",
    description=(
        "Tulsi is an aromatic perennial shrub native to the Indian subcontinent, "
        "widely cultivated across tropical and subtropical Asia. Revered in Hindu "
        "culture, it is central to Ayurvedic practice and produces small purple-white "
        "flowers and strongly aromatic leaves rich in volatile essential oils."
    ),
    native_region="Indian subcontinent; naturalised across tropical Asia and Africa",
    habitat="Tropical and subtropical climates; cultivated in household gardens and temples",
    cultivation_status="Both",
    traditional_systems=["Ayurveda", "Unani", "Siddha"],
    traditional_uses_summary=(
        "In Ayurveda, Tulsi is classified as a Rasayana and has been traditionally "
        "used for respiratory ailments including cough, cold, and bronchitis; fever; "
        "digestive complaints; and as a general tonic. Traditional use reflects "
        "cultural and historical practice and does not constitute clinical proof "
        "of efficacy."
    ),
    active_compounds=[
        ActiveCompound(
            compound_name="Eugenol",
            compound_class="Phenylpropanoid",
            primary_activity="Anti-inflammatory, antimicrobial, analgesic via COX inhibition",
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
        ),
        ActiveCompound(
            compound_name="Ursolic acid",
            compound_class="Terpenoid (Pentacyclic triterpene)",
            primary_activity="Anti-inflammatory, antioxidant, hepatoprotective in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Rosmarinic acid",
            compound_class="Polyphenol",
            primary_activity="Antioxidant, anti-inflammatory, neuroprotective in vitro",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Ocimumosides A and B",
            compound_class="Glycoside",
            primary_activity="Proposed adaptogenic and stress-axis modulating activity",
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
        ),
    ],
    therapeutic_claims=[
        TherapeuticClaim(
            condition="Stress and anxiety",
            claim_text=(
                "A small randomised controlled trial found that Tulsi leaf extract "
                "supplementation over six weeks reduced perceived stress scores and "
                "improved cognitive parameters in healthy adults."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            study_quality=StudyQuality.LOW,
            source_type="RCT (small scale)",
            citation_pmids=["23741157"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Blood glucose regulation (Type 2 diabetes)",
            claim_text=(
                "A small clinical trial reported modest reductions in fasting blood "
                "glucose with daily Tulsi leaf consumption in adults with Type 2 "
                "diabetes. Larger controlled trials are needed to confirm this finding."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            study_quality=StudyQuality.LOW,
            source_type="RCT (small scale)",
            citation_pmids=["12165191"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Respiratory tract antimicrobial activity",
            claim_text=(
                "In-vitro studies demonstrate antimicrobial activity of Tulsi essential "
                "oil against common respiratory pathogens. No controlled human clinical "
                "trials for this indication are currently available."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            study_quality=StudyQuality.UNKNOWN,
            source_type="In-Vitro",
            citation_required=False,
        ),
        TherapeuticClaim(
            condition="Anti-inflammatory activity",
            claim_text=(
                "Eugenol extracted from Tulsi demonstrates COX-2 inhibition and "
                "anti-inflammatory effects in animal models. No adequately powered "
                "human trials have confirmed this for a specific clinical indication."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            study_quality=StudyQuality.UNKNOWN,
            source_type="Animal Study",
            citation_required=False,
        ),
    ],
    evidence_summary=(
        "Tulsi's strongest human evidence covers stress reduction and modest blood "
        "glucose regulation, each supported by small-scale RCTs. Antimicrobial and "
        "anti-inflammatory claims are based on in-vitro and animal data with no "
        "adequately powered human clinical trials. Larger, well-controlled studies "
        "are needed before clinical recommendations can be made."
    ),
    preparation_methods=[
        PreparationMethod(
            method_name="Tulsi Tea (Kashayam)",
            description="Fresh or dried leaves boiled in water for 5–10 minutes and strained.",
            plant_part_used="Leaves",
            intended_use="Traditional use for cough, cold, and general wellbeing",
            safety_note=(
                "Avoid concurrent use with anticoagulants. "
                "Use caution in patients on antidiabetic medication."
            ),
        ),
        PreparationMethod(
            method_name="Standardised Leaf Extract (Capsule)",
            description=(
                "Commercial extract standardised from aerial parts. "
                "Form used in clinical trials for stress and glycaemic endpoints."
            ),
            plant_part_used="Aerial parts (standardised)",
            intended_use="Stress reduction and blood glucose management",
            safety_note="Consult physician if taking antidiabetic or anticoagulant drugs.",
        ),
    ],
    dosage_info=[
        DosageInfo(
            preparation_form="Standardised leaf extract (capsule)",
            plant_part="Aerial parts",
            route="Oral",
            population="Adults",
            dose_range_min=300,
            dose_range_max=300,
            dose_unit="mg",
            frequency="Once daily",
            max_duration="6 weeks (studied); long-term safety not established",
            is_clinical_trial_dose=True,
            evidence_source="Clinical trial",
            citation_pmids=["23741157"],
            notes="Dose used in the stress reduction RCT (PMID 23741157).",
        ),
        DosageInfo(
            preparation_form="Tea/Decoction",
            plant_part="Leaves",
            route="Oral",
            population="Adults",
            frequency="1–2 cups daily",
            max_duration="No clinical duration limit established",
            is_clinical_trial_dose=False,
            evidence_source="Traditional",
        ),
    ],
    safety_warnings=[
        SafetyWarning(
            population="Pregnant women",
            warning_type="Contraindication",
            description=(
                "Tulsi has documented uterotonic properties and has traditionally "
                "been used as an emmenagogue. Avoid during pregnancy due to risk of "
                "uterine contractions. Evidence basis is traditional knowledge and "
                "animal pharmacology."
            ),
            evidence_level=EvidenceLevel.TRADITIONAL_USE,
            citation_required=False,
        ),
        SafetyWarning(
            population="Infants and young children",
            warning_type="Advisory",
            description=(
                "Safety in children under 6 has not been established in clinical "
                "studies. Avoid high-dose preparations in this age group."
            ),
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
        SafetyWarning(
            population="Patients on anticoagulant therapy",
            warning_type="Precaution",
            description=(
                "Eugenol inhibits platelet aggregation in vitro. Concurrent use "
                "with warfarin or other anticoagulants may theoretically increase "
                "bleeding risk. Monitor if used concurrently."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        SafetyWarning(
            population="Patients on antidiabetic medication",
            warning_type="Monitoring Required",
            description=(
                "Tulsi may modestly lower fasting blood glucose. Additive effect "
                "with insulin or oral hypoglycaemics may cause hypoglycaemia. "
                "Monitor blood glucose levels if used concurrently."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmids=["12165191"],
        ),
    ],
    drug_interactions=[
        DrugInteraction(
            drug_name="Warfarin",
            drug_class="Anticoagulant (Vitamin K antagonist)",
            interaction_description=(
                "Eugenol inhibits platelet aggregation in vitro. Theoretical additive "
                "anticoagulant effect; clinical significance in humans not established."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
            severity="Moderate",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        DrugInteraction(
            drug_name="Metformin / Glibenclamide",
            drug_class="Antidiabetic",
            interaction_description=(
                "Additive blood glucose-lowering effect observed in a small clinical "
                "trial. Monitor glucose closely if used concurrently."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
            severity="Minor",
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmids=["12165191"],
        ),
    ],
    overdose_risk=(
        "Concentrated eugenol (essential oil form) is hepatotoxic at high doses. "
        "Leaf preparations at standard therapeutic doses are generally well tolerated. "
        "Do not ingest undiluted essential oil."
    ),
    regulatory_status=["AYUSH Monograph"],
    last_reviewed="2026-06-13",
    reviewer_notes=(
        "Key PMIDs in hand: 23741157 (stress RCT), 12165191 (diabetes small RCT). "
        "Respiratory and anti-inflammatory claims are preclinical only."
    ),
    who_monograph_available=False,
    ayush_monograph_available=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. NEEM  (Azadirachta indica)
# ═══════════════════════════════════════════════════════════════════════════════

NEEM = EvidenceBasedPlant(
    common_name="Neem",
    local_names=["Indian Lilac", "Nimba", "Veppu", "Margosa", "Arishta"],
    scientific_name="Azadirachta indica",
    family="Meliaceae",
    description=(
        "Neem is a fast-growing evergreen tree native to the Indian subcontinent, "
        "now widely cultivated across tropical and subtropical regions. Characterised "
        "by intensely bitter leaves and fruits, nearly every part of the tree has "
        "documented ethnobotanical uses across South Asian medical traditions. "
        "Its seed oil is used extensively in agriculture as a biopesticide."
    ),
    native_region="Indian subcontinent (India, Pakistan, Sri Lanka, Bangladesh); widely naturalised",
    habitat="Dry tropical regions; tolerates poor soils, drought, and high temperatures",
    cultivation_status="Both",
    traditional_systems=["Ayurveda", "Unani", "Siddha", "African traditional medicine"],
    traditional_uses_summary=(
        "In Ayurveda, Neem (Nimba) is traditionally used for skin diseases, fever, "
        "dental hygiene, wound healing, and as an anthelmintic. Neem twigs are used "
        "as toothbrushes in South Asian practice. Neem oil is applied topically for "
        "skin conditions. Traditional use does not establish clinical efficacy."
    ),
    active_compounds=[
        ActiveCompound(
            compound_name="Azadirachtin",
            compound_class="Terpenoid (Limonoid)",
            primary_activity="Insecticidal; disrupts insect hormonal development (agricultural use)",
            evidence_level=EvidenceLevel.STRONG_CLINICAL,
        ),
        ActiveCompound(
            compound_name="Nimbin",
            compound_class="Terpenoid (Limonoid)",
            primary_activity="Anti-inflammatory, antipyretic, antifungal in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Nimbidin",
            compound_class="Terpenoid (Limonoid)",
            primary_activity="Antibacterial, anti-ulcer activity in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Quercetin",
            compound_class="Flavonoid",
            primary_activity="Antioxidant, anti-inflammatory in vitro",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Gedunin",
            compound_class="Terpenoid (Limonoid)",
            primary_activity="Antimalarial activity in vitro against Plasmodium falciparum",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
    ],
    therapeutic_claims=[
        TherapeuticClaim(
            condition="Dental plaque and gingivitis",
            claim_text=(
                "Moderate clinical evidence supports Neem-based products for reducing "
                "dental plaque and gingivitis. Multiple small RCTs comparing Neem "
                "mouthwash and gel to chlorhexidine show comparable efficacy in plaque "
                "reduction and gingival index scores."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            study_quality=StudyQuality.MODERATE,
            source_type="RCT",
            citation_pmids=["24882626"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Skin conditions — topical (acne vulgaris)",
            claim_text=(
                "In-vitro studies demonstrate antimicrobial activity against "
                "Cutibacterium acnes. A small pilot trial reported improvement in "
                "acne with topical Neem extract. Evidence is insufficient for "
                "clinical recommendations."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            study_quality=StudyQuality.LOW,
            source_type="In-Vitro, RCT (small scale)",
            citation_required=False,
        ),
        TherapeuticClaim(
            condition="Blood glucose regulation",
            claim_text=(
                "Animal studies demonstrate hypoglycaemic effects of Neem leaf extract. "
                "The few human trials available are small and uncontrolled. Current "
                "evidence is insufficient to support clinical antidiabetic use."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            study_quality=StudyQuality.UNKNOWN,
            source_type="Animal Study",
            citation_required=False,
        ),
        TherapeuticClaim(
            condition="Wound healing — topical",
            claim_text=(
                "Neem leaf extracts demonstrate antimicrobial and anti-inflammatory "
                "properties in animal wound models. Controlled human data is absent."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            study_quality=StudyQuality.UNKNOWN,
            source_type="Animal Study",
            citation_required=False,
        ),
    ],
    evidence_summary=(
        "The strongest clinical evidence for Neem is in oral health — multiple RCTs "
        "support its use for dental plaque and gingivitis. Topical antimicrobial use "
        "for acne has limited clinical backing. Systemic claims (diabetes, wound "
        "healing) are based on preclinical data only. Oral neem oil is associated "
        "with serious toxicity in infants and must never be given to children."
    ),
    preparation_methods=[
        PreparationMethod(
            method_name="Neem Twig (Datun)",
            description="Fresh young twig used as a natural toothbrush; end chewed to expose fibres.",
            plant_part_used="Young twigs",
            intended_use="Dental hygiene — clinically studied indication",
            safety_note=None,
        ),
        PreparationMethod(
            method_name="Neem Oil (topical)",
            description="Cold-pressed seed oil applied to affected skin area.",
            plant_part_used="Seeds",
            intended_use="Topical use for skin infections and pest repellent — do not ingest",
            safety_note=(
                "NEVER administer orally. Neem oil ingestion has caused fatal "
                "toxicity in infants. For external use only."
            ),
        ),
        PreparationMethod(
            method_name="Neem Leaf Decoction (external wash)",
            description="Leaves boiled in water; cooled liquid used as a topical skin wash.",
            plant_part_used="Leaves",
            intended_use="Traditional topical use for skin conditions",
            safety_note=(
                "Internal consumption of leaf decoction at high doses has been associated "
                "with liver enzyme elevations in case reports. Use topically only."
            ),
        ),
    ],
    dosage_info=[
        DosageInfo(
            preparation_form="Neem-based mouthwash/gel",
            plant_part="Leaves or bark extract",
            route="Topical (oral cavity)",
            population="Adults",
            frequency="Twice daily (30 seconds rinse)",
            max_duration="8 weeks (studied in RCTs)",
            is_clinical_trial_dose=True,
            evidence_source="Clinical trial",
            citation_pmids=["24882626"],
            notes="Form used in dental plaque RCTs.",
        ),
        DosageInfo(
            preparation_form="Neem twig (Datun)",
            plant_part="Young twigs",
            route="Topical (oral cavity)",
            population="Adults",
            frequency="Once daily",
            max_duration="Traditional use — no clinical duration established",
            is_clinical_trial_dose=False,
            evidence_source="Traditional",
        ),
    ],
    safety_warnings=[
        SafetyWarning(
            population="Infants and young children",
            warning_type="Contraindication",
            description=(
                "Neem oil ingestion in infants and young children has caused severe "
                "acute toxicity including metabolic acidosis, seizures, and death. "
                "Neem oil must NEVER be given orally to children. This is a "
                "documented life-threatening risk."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            citation_required=True,
            citation_pmids=["11699232"],
        ),
        SafetyWarning(
            population="Pregnant women",
            warning_type="Contraindication",
            description=(
                "Neem demonstrates abortifacient properties in animal studies. "
                "Oral Neem preparations are contraindicated during pregnancy. "
                "Evidence basis is animal pharmacology and traditional knowledge."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        SafetyWarning(
            population="Patients with hepatic impairment",
            warning_type="Precaution",
            description=(
                "Case reports describe Neem-associated liver enzyme elevations "
                "following high oral doses. Monitor liver function in patients with "
                "pre-existing hepatic conditions."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=False,
        ),
    ],
    drug_interactions=[
        DrugInteraction(
            drug_name="Insulin / Metformin",
            drug_class="Antidiabetic",
            interaction_description=(
                "Additive blood glucose-lowering effect possible based on preclinical "
                "data. Monitor glucose levels if used concurrently. Clinical significance "
                "in humans not established."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
            severity="Theoretical",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        DrugInteraction(
            drug_name="Cyclosporine",
            drug_class="Calcineurin inhibitor (Immunosuppressant)",
            interaction_description=(
                "Azadirachtin may inhibit CYP3A4 in vitro, potentially increasing "
                "cyclosporine plasma concentrations. Clinical significance is unknown."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACOKINETIC_CYP,
            severity="Theoretical",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
    ],
    overdose_risk=(
        "Oral ingestion of neem oil at doses above 5 ml in infants causes metabolic "
        "acidosis, seizures, and encephalopathy — potentially fatal. High oral doses "
        "of leaf preparations in adults may cause liver enzyme elevations. Neem oil "
        "is for external use only."
    ),
    regulatory_status=["AYUSH Monograph"],
    last_reviewed="2026-06-13",
    reviewer_notes=(
        "Key PMID in hand: 24882626 (dental RCT), 11699232 (infant toxicity). "
        "Infant neem oil toxicity warning is the most critical safety gap "
        "in the existing seed data and must be present before any publishing."
    ),
    who_monograph_available=False,
    ayush_monograph_available=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ASHWAGANDHA  (Withania somnifera)
# ═══════════════════════════════════════════════════════════════════════════════

ASHWAGANDHA = EvidenceBasedPlant(
    common_name="Ashwagandha",
    local_names=["Indian Ginseng", "Winter Cherry", "Asgandh", "Vajigandha"],
    scientific_name="Withania somnifera",
    family="Solanaceae",
    description=(
        "Ashwagandha is a short perennial shrub native to the dry regions of India, "
        "North Africa, and the Mediterranean. Its fleshy roots carry a characteristic "
        "horse-like odour (Sanskrit: ashva = horse, gandha = smell). It is one of the "
        "most widely researched plants in Ayurvedic medicine and is commercially "
        "cultivated across India, particularly in Madhya Pradesh and Rajasthan."
    ),
    native_region="India, North Africa, Mediterranean; naturalised in tropical regions",
    habitat="Dry, stony subtropical soils; cultivated in arid and semi-arid agricultural regions",
    cultivation_status="Both",
    traditional_systems=["Ayurveda"],
    traditional_uses_summary=(
        "In Ayurveda, Ashwagandha root is classified as a Rasayana — a rejuvenative "
        "tonic used for debility, fatigue, impaired memory, sexual dysfunction, and "
        "as a general nervine tonic. Traditional use predates clinical evidence and "
        "should not be used to imply proven therapeutic efficacy."
    ),
    active_compounds=[
        ActiveCompound(
            compound_name="Withanolide A",
            compound_class="Steroidal lactone (Withanolide)",
            primary_activity="Anti-inflammatory, neuroprotective, immunomodulatory",
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
        ),
        ActiveCompound(
            compound_name="Withaferin A",
            compound_class="Steroidal lactone (Withanolide)",
            primary_activity="Apoptosis induction in cancer cell lines (preclinical only)",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Withanolide D",
            compound_class="Steroidal lactone (Withanolide)",
            primary_activity="Immunostimulatory activity in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Sitoindosides VII–X",
            compound_class="Glycowithanolide",
            primary_activity="Proposed adaptogenic and cognitive-enhancing activity",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Withanine",
            compound_class="Alkaloid",
            primary_activity="Sedative and antistress effects in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
    ],
    therapeutic_claims=[
        TherapeuticClaim(
            condition="Stress and anxiety reduction",
            claim_text=(
                "A meta-analysis and multiple RCTs confirm that standardised "
                "Ashwagandha root extract (300–600 mg/day, KSM-66 or equivalent) "
                "significantly reduces perceived stress, anxiety, and serum cortisol "
                "in adults with chronic stress compared to placebo."
            ),
            evidence_level=EvidenceLevel.STRONG_CLINICAL,
            study_quality=StudyQuality.HIGH,
            source_type="Meta-Analysis, RCT",
            citation_pmids=["31517876"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Sleep quality",
            claim_text=(
                "A double-blind RCT found that Ashwagandha root extract improved "
                "sleep quality, sleep onset latency, and total sleep time in adults "
                "with insomnia compared to placebo over 8 weeks."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            study_quality=StudyQuality.MODERATE,
            source_type="RCT",
            citation_pmids=["32540634"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Muscle strength and exercise performance",
            claim_text=(
                "An RCT in resistance-trained adults found that Ashwagandha "
                "supplementation significantly improved muscle strength, muscle "
                "recovery, and VO2 max compared to placebo over 8 weeks."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            study_quality=StudyQuality.MODERATE,
            source_type="RCT",
            citation_pmids=["25624699"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Male infertility and testosterone",
            claim_text=(
                "A small RCT reported improvements in sperm count, sperm motility, "
                "and serum testosterone in infertile men supplemented with Ashwagandha "
                "root extract for 3 months. Larger replication studies are needed."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            study_quality=StudyQuality.LOW,
            source_type="RCT (small scale)",
            citation_pmids=["23796876"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Cognitive function and memory",
            claim_text=(
                "A small RCT found improved cognitive performance, reaction time, "
                "and memory in healthy adults receiving Ashwagandha extract "
                "compared to placebo. Study was short-term and small."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            study_quality=StudyQuality.LOW,
            source_type="RCT (small scale)",
            citation_pmids=["27055824"],
            citation_required=True,
        ),
    ],
    evidence_summary=(
        "Ashwagandha has the strongest clinical evidence among the plants in this "
        "dataset. Stress and anxiety reduction is supported by a meta-analysis and "
        "multiple RCTs. Sleep quality and athletic performance have moderate evidence "
        "from individual RCTs. Fertility and cognitive claims are supported by small "
        "trials requiring replication. The KSM-66 and Sensoril standardised root "
        "extracts were used in most clinical trials."
    ),
    preparation_methods=[
        PreparationMethod(
            method_name="Standardised Root Extract (KSM-66 / Sensoril)",
            description=(
                "Concentrated root extract standardised to ≥5% withanolides. "
                "Form used in clinical trials. Available as capsules or tablets."
            ),
            plant_part_used="Root (standardised extract)",
            intended_use="Stress, sleep, performance — evidence-based form",
            safety_note=(
                "Consult physician if taking thyroid medication, immunosuppressants, "
                "or CNS sedatives. Contraindicated in pregnancy."
            ),
        ),
        PreparationMethod(
            method_name="Ashwagandha Churna (Powder)",
            description="Dried root powder mixed with warm milk, honey, or ghee. Traditional Ayurvedic preparation.",
            plant_part_used="Dried root",
            intended_use="Traditional adaptogenic and tonic use",
            safety_note="Avoid in pregnancy. Monitor thyroid function if on levothyroxine.",
        ),
    ],
    dosage_info=[
        DosageInfo(
            preparation_form="Standardised root extract (KSM-66 capsule)",
            plant_part="Root",
            route="Oral",
            population="Adults",
            dose_range_min=300,
            dose_range_max=600,
            dose_unit="mg",
            frequency="Once or twice daily",
            max_duration="12 weeks (studied); longer term data limited",
            is_clinical_trial_dose=True,
            evidence_source="Clinical trial",
            citation_pmids=["31517876", "32540634", "25624699"],
            notes="300 mg twice daily and 600 mg once daily both used in RCTs.",
        ),
        DosageInfo(
            preparation_form="Root powder (Churna)",
            plant_part="Root",
            route="Oral",
            population="Adults",
            dose_range_min=3,
            dose_range_max=6,
            dose_unit="g",
            frequency="Once or twice daily with milk",
            max_duration="Traditional use — no clinical duration established for this form",
            is_clinical_trial_dose=False,
            evidence_source="Traditional",
        ),
    ],
    safety_warnings=[
        SafetyWarning(
            population="Pregnant women",
            warning_type="Contraindication",
            description=(
                "Ashwagandha has documented uterotonic and abortifacient properties "
                "in traditional knowledge and animal models. Contraindicated throughout "
                "pregnancy. Avoid entirely."
            ),
            evidence_level=EvidenceLevel.TRADITIONAL_USE,
            citation_required=False,
        ),
        SafetyWarning(
            population="Patients on thyroid hormone replacement (levothyroxine)",
            warning_type="Monitoring Required",
            description=(
                "Ashwagandha may increase serum T3 and T4 levels. Concurrent use "
                "with levothyroxine may cause hyperthyroid symptoms. Monitor TSH "
                "levels if used concurrently."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmids=["28829155"],
        ),
        SafetyWarning(
            population="Patients on immunosuppressant therapy",
            warning_type="Precaution",
            description=(
                "Immunomodulatory properties may potentially counteract "
                "immunosuppressive therapy in transplant patients. Use only "
                "under physician supervision."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        SafetyWarning(
            population="Patients on CNS sedatives or benzodiazepines",
            warning_type="Precaution",
            description=(
                "Ashwagandha has sedative properties (proposed GABA-A receptor "
                "modulation). Additive sedation with CNS depressants is possible. "
                "Monitor for excessive sedation if used concurrently."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        SafetyWarning(
            population="Infants and children",
            warning_type="Advisory",
            description=(
                "Safety in paediatric populations has not been established in "
                "clinical studies. Avoid use in children."
            ),
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
    ],
    drug_interactions=[
        DrugInteraction(
            drug_name="Levothyroxine",
            drug_class="Thyroid hormone replacement",
            interaction_description=(
                "Ashwagandha may increase serum thyroid hormone levels. Concurrent "
                "use with levothyroxine risks hyperthyroidism. Monitor TSH."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
            severity="Moderate",
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmids=["28829155"],
        ),
        DrugInteraction(
            drug_name="Lorazepam / Diazepam",
            drug_class="Benzodiazepine (CNS depressant)",
            interaction_description=(
                "Additive sedation possible. Ashwagandha has proposed GABA-A "
                "modulatory activity. Monitor for excess sedation if combined."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
            severity="Minor",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        DrugInteraction(
            drug_name="Cyclosporine / Tacrolimus",
            drug_class="Immunosuppressant (calcineurin inhibitor)",
            interaction_description=(
                "Theoretical risk that immunostimulatory activity may reduce "
                "efficacy of immunosuppressive therapy. No clinical data available."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ANT,
            severity="Theoretical",
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
    ],
    overdose_risk=(
        "High doses (>6 g root powder/day) have caused gastrointestinal distress, "
        "nausea, and diarrhoea. Isolated case reports of liver injury exist, typically "
        "with adulterated or excessively high-dose products. Liver enzyme monitoring "
        "is recommended for long-term high-dose use."
    ),
    regulatory_status=["AYUSH Monograph"],
    last_reviewed="2026-06-13",
    reviewer_notes=(
        "All 6 core PMIDs in hand: 31517876 (stress meta-analysis), 32540634 (sleep), "
        "25624699 (performance), 23796876 (fertility), 27055824 (cognitive), "
        "28829155 (thyroid). Thyroid stimulation is both a therapeutic claim and "
        "a safety risk — documented in both sections."
    ),
    who_monograph_available=False,
    ayush_monograph_available=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. TURMERIC  (Curcuma longa)
# ═══════════════════════════════════════════════════════════════════════════════

TURMERIC = EvidenceBasedPlant(
    common_name="Turmeric",
    local_names=["Haldi", "Manjal", "Pasupu", "Haridra", "Indian Saffron"],
    scientific_name="Curcuma longa",
    family="Zingiberaceae",
    description=(
        "Turmeric is a perennial rhizomatous herb native to South and Southeast Asia. "
        "Its orange-yellow rhizome is the source of curcumin, the principal "
        "curcuminoid responsible for its colour and many of its studied biological "
        "activities. Widely used as a culinary spice across Asia, turmeric is one "
        "of the most researched botanical ingredients globally."
    ),
    native_region="South and Southeast Asia (India, Sri Lanka, Southeast Asia)",
    habitat="Tropical and subtropical humid climates; cultivated in well-drained fertile soils",
    cultivation_status="Cultivated",
    traditional_systems=["Ayurveda", "Unani", "Siddha", "Traditional Chinese Medicine"],
    traditional_uses_summary=(
        "In Ayurveda, turmeric (Haridra) has been traditionally used for wound "
        "healing, skin disorders, digestive complaints, joint pain, and as a general "
        "anti-inflammatory agent. It is also a widely used dietary spice and food "
        "colouring. Traditional use should not be equated with clinical proof "
        "of therapeutic efficacy."
    ),
    active_compounds=[
        ActiveCompound(
            compound_name="Curcumin",
            compound_class="Polyphenol (Diarylheptanoid / Curcuminoid)",
            primary_activity="Anti-inflammatory (NF-κB inhibition), antioxidant, COX-2 inhibition",
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
        ),
        ActiveCompound(
            compound_name="Bisdemethoxycurcumin",
            compound_class="Polyphenol (Curcuminoid)",
            primary_activity="Antioxidant, anti-inflammatory (less studied than curcumin)",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="ar-Turmerone",
            compound_class="Terpenoid (Sesquiterpene)",
            primary_activity="Anti-inflammatory, neuroprotective in vitro",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Turmerone",
            compound_class="Terpenoid (Sesquiterpene)",
            primary_activity="Antifungal, anti-inflammatory in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
    ],
    therapeutic_claims=[
        TherapeuticClaim(
            condition="Osteoarthritis knee pain",
            claim_text=(
                "A meta-analysis of RCTs found that curcumin supplementation "
                "significantly reduced pain and improved function in patients "
                "with knee osteoarthritis compared to placebo. Effect size was "
                "clinically meaningful in several trials."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            study_quality=StudyQuality.HIGH,
            source_type="Meta-Analysis, RCT",
            citation_pmids=["29867540"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Ulcerative colitis (maintenance of remission)",
            claim_text=(
                "A small double-blind RCT found that curcumin as adjunctive therapy "
                "to mesalazine significantly reduced relapse rate in patients with "
                "quiescent ulcerative colitis compared to placebo."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            study_quality=StudyQuality.LOW,
            source_type="RCT (small scale)",
            citation_pmids=["16891638"],
            citation_required=True,
        ),
        TherapeuticClaim(
            condition="Metabolic syndrome parameters",
            claim_text=(
                "Small clinical trials suggest curcumin may modestly improve "
                "blood glucose, lipid profiles, and waist circumference in "
                "adults with metabolic syndrome. Results are preliminary."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            study_quality=StudyQuality.LOW,
            source_type="RCT (small scale)",
            citation_required=False,
        ),
        TherapeuticClaim(
            condition="Antioxidant and anti-inflammatory activity",
            claim_text=(
                "Curcumin inhibits NF-κB, COX-2, and iNOS pathways in vitro and "
                "in animal models. These preclinical findings inform the rationale "
                "for clinical trials but do not constitute human clinical evidence."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            study_quality=StudyQuality.UNKNOWN,
            source_type="In-Vitro, Animal Study",
            citation_required=False,
        ),
    ],
    evidence_summary=(
        "Turmeric's strongest evidence is for osteoarthritis knee pain, supported "
        "by a meta-analysis of RCTs. Ulcerative colitis maintenance has limited "
        "clinical backing from one small RCT. Metabolic syndrome effects are "
        "preliminary. Preclinical anti-inflammatory data is extensive but does not "
        "substitute for human clinical trials. Oral bioavailability of curcumin is "
        "poor; clinical trial formulations use enhanced bioavailability forms "
        "(piperine combinations or lipid formulations)."
    ),
    preparation_methods=[
        PreparationMethod(
            method_name="Curcumin Extract (enhanced bioavailability)",
            description=(
                "Standardised curcumin extract, typically combined with piperine "
                "(black pepper extract) or in a lipid formulation to improve "
                "oral bioavailability."
            ),
            plant_part_used="Rhizome (standardised extract)",
            intended_use="Osteoarthritis, anti-inflammatory — evidence-based form",
            safety_note=(
                "Avoid in patients with bile duct obstruction or gallstones. "
                "Inform physician if on anticoagulants or antidiabetics."
            ),
        ),
        PreparationMethod(
            method_name="Turmeric Paste (Golden Paste)",
            description=(
                "Ground turmeric rhizome mixed with a small amount of black pepper "
                "and fat (e.g., coconut oil) to form a paste. Traditional preparation."
            ),
            plant_part_used="Fresh or dried rhizome",
            intended_use="Traditional dietary and topical anti-inflammatory use",
            safety_note="Avoid high doses (>1 tsp/day as supplement) in pregnancy.",
        ),
    ],
    dosage_info=[
        DosageInfo(
            preparation_form="Curcumin extract with piperine (capsule)",
            plant_part="Rhizome",
            route="Oral",
            population="Adults",
            dose_range_min=500,
            dose_range_max=1000,
            dose_unit="mg",
            frequency="Twice daily with meals",
            max_duration="12 weeks (studied); data beyond 3 months limited",
            is_clinical_trial_dose=True,
            evidence_source="Clinical trial",
            citation_pmids=["29867540"],
            notes="Curcumin combined with piperine (BioPerine) used in most OA trials.",
        ),
        DosageInfo(
            preparation_form="Dietary spice (culinary use)",
            plant_part="Dried rhizome powder",
            route="Oral",
            population="General population",
            dose_range_min=1,
            dose_range_max=3,
            dose_unit="g",
            frequency="Daily as part of diet",
            max_duration="No limit for culinary use",
            is_clinical_trial_dose=False,
            evidence_source="Traditional",
            notes="Culinary doses are far below supplemental doses used in trials.",
        ),
    ],
    safety_warnings=[
        SafetyWarning(
            population="Patients with bile duct obstruction or gallstones",
            warning_type="Contraindication",
            description=(
                "Curcumin is a potent cholagogue — it stimulates bile secretion. "
                "This is contraindicated in patients with bile duct obstruction "
                "or active gallstones, as it may worsen obstruction or trigger "
                "biliary colic."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=False,
        ),
        SafetyWarning(
            population="Pregnant women",
            warning_type="Precaution",
            description=(
                "High-dose curcumin supplements should be avoided in pregnancy as "
                "pharmacological doses may stimulate uterine contractions. Culinary "
                "use of turmeric as a spice is generally considered safe."
            ),
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
        SafetyWarning(
            population="Infants and young children",
            warning_type="Advisory",
            description=(
                "Supplemental curcumin has not been studied in infants or young "
                "children. Avoid high-dose preparations. Dietary use in food is "
                "generally considered safe."
            ),
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
        SafetyWarning(
            population="Patients with kidney stones (calcium oxalate)",
            warning_type="Advisory",
            description=(
                "Turmeric is high in oxalates. High supplemental doses may increase "
                "urinary oxalate excretion and risk of calcium oxalate stones in "
                "susceptible individuals."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=False,
        ),
    ],
    drug_interactions=[
        DrugInteraction(
            drug_name="Warfarin / Clopidogrel",
            drug_class="Anticoagulant / Antiplatelet",
            interaction_description=(
                "Curcumin inhibits platelet aggregation and may theoretically "
                "potentiate anticoagulant or antiplatelet effects, increasing "
                "bleeding risk. Clinical cases are rare but monitor INR."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACOKINETIC_CYP,
            severity="Moderate",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        DrugInteraction(
            drug_name="Insulin / Oral antidiabetics",
            drug_class="Antidiabetic",
            interaction_description=(
                "Curcumin may lower blood glucose via AMPK activation. Additive "
                "effect with antidiabetic drugs may cause hypoglycaemia. "
                "Monitor glucose if used concurrently."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
            severity="Minor",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
    ],
    overdose_risk=(
        "High-dose curcumin supplements (>8 g/day) have caused nausea, diarrhoea, "
        "and abdominal cramping. Kidney stone formation is a risk with chronic "
        "high-dose use in susceptible individuals. Dietary use as a spice is safe."
    ),
    regulatory_status=["AYUSH Monograph", "FDA GRAS (as food ingredient)"],
    last_reviewed="2026-06-13",
    reviewer_notes=(
        "Key PMIDs in hand: 29867540 (OA meta-analysis), 16891638 (UC RCT). "
        "Bile duct contraindication is the most important safety flag — "
        "widely cited in herbal pharmacognosy but often omitted in popular content."
    ),
    who_monograph_available=False,
    ayush_monograph_available=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. BAEL  (Aegle marmelos)
# ═══════════════════════════════════════════════════════════════════════════════

BAEL = EvidenceBasedPlant(
    common_name="Bael",
    local_names=["Bengal Quince", "Bilva", "Bel", "Vilvam", "Stone Apple"],
    scientific_name="Aegle marmelos",
    family="Rutaceae",
    description=(
        "Bael is a medium-sized deciduous tree native to the Indian subcontinent "
        "and Southeast Asia, sacred in Hindu tradition and associated with Lord Shiva. "
        "Its hard-shelled woody fruit contains an aromatic mucilaginous pulp used "
        "in food and medicine. Both the fruit and leaves have documented "
        "ethnobotanical and pharmacological properties."
    ),
    native_region="Indian subcontinent and Southeast Asia; cultivated in tropical regions",
    habitat="Tropical dry forests, scrublands; tolerates drought and dry sandy soils",
    cultivation_status="Both",
    traditional_systems=["Ayurveda", "Siddha", "Unani"],
    traditional_uses_summary=(
        "In Ayurveda, Bael fruit (Bilva) is traditionally used for acute and "
        "chronic diarrhoea, dysentery, and digestive complaints. The dried unripe "
        "fruit is considered particularly effective for gastrointestinal conditions. "
        "Leaves are used topically for eye and skin conditions, and the root bark "
        "is used in fever management. Traditional use does not constitute clinical "
        "proof of efficacy."
    ),
    active_compounds=[
        ActiveCompound(
            compound_name="Marmelosin (Imperatorin)",
            compound_class="Furanocoumarin",
            primary_activity="Antidiarrheal, antimicrobial, antifungal activity in vitro",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Lupeol",
            compound_class="Terpenoid (Pentacyclic triterpene)",
            primary_activity="Anti-inflammatory, antidiabetic in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Umbelliferone",
            compound_class="Coumarin",
            primary_activity="Antimicrobial, anti-inflammatory, antioxidant in vitro",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Aegelin",
            compound_class="Amide alkaloid",
            primary_activity="Antifungal, antibacterial activity in vitro",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
    ],
    therapeutic_claims=[
        TherapeuticClaim(
            condition="Acute diarrhoea and dysentery",
            claim_text=(
                "Limited clinical evidence from small trials in India suggests that "
                "dried unripe Bael fruit powder may reduce stool frequency and "
                "duration in acute diarrhoea and dysentery. Evidence quality is "
                "low; larger controlled trials are required."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            study_quality=StudyQuality.LOW,
            source_type="RCT (small scale)",
            citation_required=True,
            citation_pmids=[],
            citation_flag_reason=(
                "Small clinical trials documented in Indian pharmacological literature. "
                "PubMed-indexed PMID pending verification — to be added before publishing."
            ),
        ),
        TherapeuticClaim(
            condition="Blood glucose regulation",
            claim_text=(
                "Animal studies demonstrate antidiabetic effects of Bael leaf extract, "
                "including improved insulin sensitivity. No controlled human trials "
                "are currently available to support clinical antidiabetic use."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            study_quality=StudyQuality.UNKNOWN,
            source_type="Animal Study",
            citation_required=False,
        ),
        TherapeuticClaim(
            condition="Antimicrobial activity",
            claim_text=(
                "In-vitro studies show activity of Bael extracts and isolated "
                "marmelosin against gram-positive and gram-negative bacteria and "
                "selected fungi. Clinical translation has not been studied."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            study_quality=StudyQuality.UNKNOWN,
            source_type="In-Vitro",
            citation_required=False,
        ),
        TherapeuticClaim(
            condition="Hepatoprotective activity",
            claim_text=(
                "Animal studies report hepatoprotective effects of Bael fruit extract "
                "against carbon tetrachloride-induced liver damage. No human clinical "
                "evidence is available."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            study_quality=StudyQuality.UNKNOWN,
            source_type="Animal Study",
            citation_required=False,
        ),
    ],
    evidence_summary=(
        "Bael's strongest evidence base is the traditional and limited clinical "
        "record for diarrhoea and dysentery, particularly in Ayurvedic practice. "
        "A small number of clinical trials exist in Indian pharmacological "
        "literature but are limited by scale and methodological quality. "
        "Antidiabetic, antimicrobial, and hepatoprotective claims are based "
        "on preclinical data only. Larger, well-controlled RCTs are needed."
    ),
    preparation_methods=[
        PreparationMethod(
            method_name="Dried Unripe Fruit Powder (Bilva Churna)",
            description=(
                "Dried unripe Bael fruit pulp ground to a powder. "
                "Prepared as a decoction or mixed with water."
            ),
            plant_part_used="Unripe fruit (dried)",
            intended_use="Traditional use for diarrhoea and dysentery",
            safety_note="Monitor blood glucose in diabetic patients on antidiabetic medication.",
        ),
        PreparationMethod(
            method_name="Bael Sharbat (Ripe Fruit Drink)",
            description=(
                "Ripe fruit pulp diluted with water and strained. Consumed as a "
                "cooling beverage and traditional digestive aid."
            ),
            plant_part_used="Ripe fruit pulp",
            intended_use="Traditional digestive tonic and cooling drink",
            safety_note=None,
        ),
    ],
    dosage_info=[
        DosageInfo(
            preparation_form="Dried unripe fruit powder",
            plant_part="Unripe fruit",
            route="Oral",
            population="Adults",
            dose_range_min=5,
            dose_range_max=10,
            dose_unit="g",
            frequency="Twice daily",
            max_duration="Up to 7 days for acute diarrhoea (traditional practice)",
            is_clinical_trial_dose=False,
            evidence_source="Traditional",
            notes="Form used in small Indian clinical trials but exact dose varies.",
        ),
        DosageInfo(
            preparation_form="Ripe fruit pulp drink",
            plant_part="Ripe fruit",
            route="Oral",
            population="Adults",
            frequency="Once daily",
            max_duration="No established limit for dietary use",
            is_clinical_trial_dose=False,
            evidence_source="Traditional",
        ),
    ],
    safety_warnings=[
        SafetyWarning(
            population="Pregnant women",
            warning_type="Advisory",
            description=(
                "Pharmacological doses of Bael preparations have not been studied "
                "in pregnancy. As a precautionary measure, avoid high-dose Bael "
                "preparations during pregnancy. Dietary fruit consumption is "
                "traditionally considered safe."
            ),
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
        SafetyWarning(
            population="Patients on antidiabetic medication",
            warning_type="Monitoring Required",
            description=(
                "Bael leaf extract has demonstrated antidiabetic effects in animal "
                "models. Additive blood glucose-lowering effect with antidiabetic "
                "drugs is possible. Monitor glucose if used concurrently."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
        SafetyWarning(
            population="Infants and young children",
            warning_type="Advisory",
            description=(
                "Safety of Bael preparations in infants and young children has "
                "not been established. Dietary use of fruit pulp is traditional "
                "but pharmacological preparations should be avoided."
            ),
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
    ],
    drug_interactions=[
        DrugInteraction(
            drug_name="Insulin / Oral antidiabetics",
            drug_class="Antidiabetic",
            interaction_description=(
                "Theoretical additive hypoglycaemic effect based on preclinical "
                "antidiabetic data. Monitor blood glucose if used concurrently."
            ),
            interaction_mechanism=InteractionMechanism.PHARMACODYNAMIC_ADD,
            severity="Theoretical",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=False,
        ),
    ],
    overdose_risk=(
        "No documented toxicity at normal therapeutic doses. The hard outer shell "
        "of the fruit is not consumed. High doses of tannin-rich preparations may "
        "cause constipation."
    ),
    regulatory_status=["AYUSH Monograph"],
    last_reviewed="2026-06-13",
    reviewer_notes=(
        "Antidiarrheal PMID is pending verification from Indian pharmacological "
        "literature. All other claims are preclinical or traditional. "
        "review_status will be PENDING until PMID is resolved."
    ),
    who_monograph_available=False,
    ayush_monograph_available=True,
)


# ── Export list ────────────────────────────────────────────────────────────────

PILOT_PLANTS = [TULSI, NEEM, ASHWAGANDHA, TURMERIC, BAEL]
