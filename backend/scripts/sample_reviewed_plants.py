"""
Evidence-Based Plant Data — 3 Sample Reviews
==============================================
Applies the EvidenceBasedPlant schema to Tulsi, Neem, and Ashwagandha.
Each entry documents:
- Every therapeutic claim with its evidence level
- Compounds with compound class
- Typed safety warnings (Contraindication vs Precaution)
- Drug interactions with severity
- Explicit citation flags for unverified claims

Run this file to validate all 3 plants against the schema:
    python backend/scripts/sample_reviewed_plants.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.evidence_schema import (
    EvidenceBasedPlant, EvidenceLevel, SafetyClass, ReviewStatus,
    TherapeuticClaim, DrugInteraction, SafetyWarning,
    ActiveCompound, PreparationMethod, REVIEW_CHECKLIST
)


# ═══════════════════════════════════════════════════════════════════════════════
# PLANT 1 — TULSI (Holy Basil)
# ═══════════════════════════════════════════════════════════════════════════════

TULSI = EvidenceBasedPlant(
    # ── Identity ──────────────────────────────────────────────────────────────
    common_name="Tulsi",
    local_names=["Holy Basil", "Sacred Basil", "Tulasi", "Vrinda"],
    scientific_name="Ocimum tenuiflorum",
    family="Lamiaceae",
    description=(
        "Tulsi is an aromatic perennial shrub native to the Indian subcontinent. "
        "It is one of the most venerated plants in Ayurvedic medicine and Hindu culture, "
        "commonly grown in household gardens. The plant produces small purple-white flowers "
        "and strongly aromatic leaves containing volatile oils."
    ),

    # ── Geography ─────────────────────────────────────────────────────────────
    native_region="Indian subcontinent; widely naturalised across tropical regions",
    habitat="Tropical and subtropical climates; cultivated in gardens, temples, and farms",
    cultivation_status="Both",

    # ── Phytochemistry ────────────────────────────────────────────────────────
    active_compounds=[
        ActiveCompound(
            compound_name="Eugenol",
            compound_class="Phenylpropanoid",
            primary_activity="Anti-inflammatory, antimicrobial, analgesic",
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
        ),
        ActiveCompound(
            compound_name="Ursolic acid",
            compound_class="Terpenoid (Pentacyclic triterpene)",
            primary_activity="Anti-inflammatory, antioxidant, hepatoprotective",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Rosmarinic acid",
            compound_class="Polyphenol",
            primary_activity="Antioxidant, anti-inflammatory, neuroprotective",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Ocimumosides A and B",
            compound_class="Glycoside",
            primary_activity="Adaptogenic activity — proposed stress-modulating properties",
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
        ),
    ],

    # ── Traditional Use ───────────────────────────────────────────────────────
    traditional_system="Ayurveda, Unani, Siddha",
    traditional_uses_summary=(
        "In Ayurveda, Tulsi (classified as 'Rasayana') has been traditionally used for "
        "respiratory ailments including cough, cold, asthma, and bronchitis; for fever, "
        "digestive complaints, and stress. It holds religious significance in Vaishnavism. "
        "Traditional use should not be interpreted as clinical proof of efficacy."
    ),

    # ── Therapeutic Claims ────────────────────────────────────────────────────
    therapeutic_claims=[
        TherapeuticClaim(
            condition="Stress and anxiety (adaptogenic use)",
            claim_text=(
                "Limited clinical evidence suggests Tulsi leaf extract may reduce "
                "perceived stress and anxiety in healthy adults, with effects observed "
                "in small-scale RCTs."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            source_type="RCT (small scale)",
            citation_required=True,
            citation_pmid="23741157",
            citation_flag_reason=None,
        ),
        TherapeuticClaim(
            condition="Type 2 diabetes — blood glucose regulation",
            claim_text=(
                "Limited clinical evidence from small trials suggests that Tulsi leaf "
                "extract may modestly reduce fasting blood glucose. Effect size and "
                "long-term safety in diabetic populations require further study."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            source_type="RCT (small scale)",
            citation_required=True,
            citation_pmid="12165191",
            citation_flag_reason=None,
        ),
        TherapeuticClaim(
            condition="Respiratory infections (upper tract)",
            claim_text=(
                "Traditionally used for coughs and colds. Laboratory studies show "
                "antimicrobial activity of Tulsi essential oil against common respiratory "
                "pathogens, but controlled clinical trials in humans are lacking."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            source_type="In-Vitro, Traditional/Ayurvedic",
            citation_required=True,
            citation_pmid=None,
            citation_flag_reason=(
                "Claim uses in-vitro data but is for a clinical indication. "
                "Need RCT or at minimum observational study PMID."
            ),
        ),
        TherapeuticClaim(
            condition="Immunomodulation",
            claim_text=(
                "Animal and in-vitro studies suggest Tulsi extracts may modulate "
                "immune parameters. Human clinical evidence is insufficient to make "
                "therapeutic claims."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            source_type="Animal Study, In-Vitro",
            citation_required=True,
            citation_pmid=None,
            citation_flag_reason=(
                "Often described as 'immune booster' in seed data — this is a BANNED_PHRASE. "
                "Must be replaced with evidence-qualified language and a PMID."
            ),
        ),
        TherapeuticClaim(
            condition="Anti-inflammatory activity",
            claim_text=(
                "Eugenol in Tulsi has demonstrated anti-inflammatory activity comparable "
                "to ibuprofen in animal models (COX inhibition). Human clinical evidence "
                "for this mechanism is currently preclinical."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            source_type="Animal Study",
            citation_required=True,
            citation_pmid=None,
            citation_flag_reason="Animal model data. Need human trial PMID to upgrade evidence level.",
        ),
    ],

    # ── Overall Evidence ──────────────────────────────────────────────────────
    overall_evidence_strength=EvidenceLevel.LIMITED_CLINICAL,
    evidence_summary=(
        "Tulsi has a strong traditional use record and promising preclinical data. "
        "The most robust human evidence is for adaptogenic (stress-reducing) effects "
        "and modest blood glucose modulation, both supported by small-scale RCTs. "
        "Immunomodulatory and respiratory claims are currently supported only by "
        "in-vitro and animal studies. Larger, well-powered RCTs are needed before "
        "clinical recommendations can be made."
    ),

    # ── Preparation Methods ───────────────────────────────────────────────────
    preparation_methods=[
        PreparationMethod(
            method_name="Tulsi Tea (Kashayam)",
            description="Fresh or dried leaves boiled in water for 5–10 minutes, strained and consumed.",
            plant_part_used="Leaves",
            intended_use="Cough, cold, general wellbeing — traditional use",
            safety_note="Avoid in pregnancy; do not use with anticoagulants.",
        ),
        PreparationMethod(
            method_name="Fresh Leaf Juice",
            description="Fresh leaves ground and juice extracted; typically 5–10 ml per dose.",
            plant_part_used="Leaves",
            intended_use="Traditional use for fever and respiratory symptoms",
            safety_note="Concentrated eugenol content; avoid prolonged high-dose use.",
        ),
        PreparationMethod(
            method_name="Standardised Extract (capsule/tablet)",
            description="Commercial standardised extract, dose as per manufacturer.",
            plant_part_used="Aerial parts (standardised)",
            intended_use="Stress, blood glucose management (clinical studies used this form)",
            safety_note="Consult physician if on antidiabetic or anticoagulant medication.",
        ),
    ],

    # ── Safety ────────────────────────────────────────────────────────────────
    safety_class=SafetyClass.USE_WITH_CAUTION,
    safety_warnings=[
        SafetyWarning(
            population="Pregnant women",
            warning_type="Contraindication",
            description=(
                "Tulsi has documented uterotonic properties and has been used "
                "traditionally as an emmenagogue. Avoid during pregnancy — risk of "
                "uterine contractions."
            ),
            evidence_level=EvidenceLevel.TRADITIONAL_USE,
            citation_required=True,
            citation_pmid=None,
        ),
        SafetyWarning(
            population="Patients on anticoagulants (warfarin, aspirin)",
            warning_type="Precaution",
            description=(
                "Eugenol inhibits platelet aggregation. Concurrent use with anticoagulants "
                "or antiplatelet drugs may increase bleeding risk."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=True,
            citation_pmid=None,
        ),
        SafetyWarning(
            population="Patients on antidiabetic medication",
            warning_type="Monitoring Required",
            description=(
                "Tulsi may modestly lower blood glucose. Concurrent use with insulin "
                "or oral hypoglycaemics may cause additive hypoglycaemia."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmid="12165191",
        ),
        SafetyWarning(
            population="Infants and young children",
            warning_type="Advisory",
            description=(
                "Safety in infants and children under 6 has not been established in "
                "clinical studies. Avoid high-dose preparations."
            ),
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
    ],
    drug_interactions=[
        DrugInteraction(
            drug_name="Warfarin",
            drug_class="Anticoagulant",
            interaction_description=(
                "Eugenol in Tulsi inhibits platelet aggregation and may potentiate "
                "the anticoagulant effect of warfarin, increasing bleeding risk."
            ),
            severity="Moderate",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=True,
            citation_pmid=None,
        ),
        DrugInteraction(
            drug_name="Metformin / Glibenclamide",
            drug_class="Antidiabetic",
            interaction_description=(
                "Additive blood glucose-lowering effect possible. Monitor glucose "
                "levels closely if used concurrently."
            ),
            severity="Minor",
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmid="12165191",
        ),
    ],
    overdose_risk=(
        "High-dose eugenol (concentrated oil) is hepatotoxic. Avoid undiluted "
        "essential oil internally. Leaf preparations at culinary doses are generally well tolerated."
    ),

    # ── Review Metadata ───────────────────────────────────────────────────────
    review_status=ReviewStatus.FLAGGED,
    claims_requiring_citation=[
        "Respiratory infections: In-vitro antimicrobial data used for a clinical indication — needs RCT PMID",
        "Immunomodulation: 'Immune booster' language must be removed; preclinical PMID required",
        "Anti-inflammatory: Animal COX-inhibition data — needs human PMID to upgrade",
        "Pregnancy contraindication: Uterotonic evidence needs a pharmacological or case report PMID",
        "Warfarin interaction: Needs pharmacodynamic study PMID",
    ],
    flagged_issues=[
        "Seed data uses 'immune booster' — BANNED_PHRASE, must be rewritten",
        "Seed data says 'highly beneficial' — BANNED_PHRASE, must be removed",
        "Seed data does not distinguish traditional use from clinical evidence",
        "No preclinical / clinical separation in current flat-text schema",
    ],
    reviewer_notes=(
        "Tulsi is one of the more studied Indian medicinal plants. "
        "The stress-reduction and glycaemic evidence, though small-scale, is real. "
        "Priority PMIDs: 23741157 (stress RCT), 12165191 (diabetes RCT). "
        "All immunomodulation and 'blood purification' language must be removed."
    ),
    who_monograph_available=False,
    ayush_monograph_available=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# PLANT 2 — NEEM
# ═══════════════════════════════════════════════════════════════════════════════

NEEM = EvidenceBasedPlant(
    # ── Identity ──────────────────────────────────────────────────────────────
    common_name="Neem",
    local_names=["Nimba", "Indian Lilac", "Veppu", "Margosa", "Arishta"],
    scientific_name="Azadirachta indica",
    family="Meliaceae",
    description=(
        "Neem is a fast-growing evergreen tree native to the Indian subcontinent, "
        "now cultivated widely across tropical and subtropical regions. Known for its "
        "intensely bitter taste, nearly every part of the tree — bark, leaves, seeds, "
        "flowers, and roots — has documented ethnobotanical uses across South and "
        "Southeast Asian medical traditions."
    ),

    # ── Geography ─────────────────────────────────────────────────────────────
    native_region="Indian subcontinent (India, Pakistan, Sri Lanka, Bangladesh)",
    habitat="Dry tropical regions; tolerates poor soils and drought",
    cultivation_status="Both",

    # ── Phytochemistry ────────────────────────────────────────────────────────
    active_compounds=[
        ActiveCompound(
            compound_name="Azadirachtin",
            compound_class="Terpenoid (Limonoid)",
            primary_activity="Insecticidal, antifeedant; disrupts insect hormone systems",
            evidence_level=EvidenceLevel.STRONG_CLINICAL,  # Strong for agricultural/pesticidal use
        ),
        ActiveCompound(
            compound_name="Nimbin",
            compound_class="Terpenoid (Limonoid)",
            primary_activity="Anti-inflammatory, antipyretic, antifungal",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Nimbidin",
            compound_class="Terpenoid (Limonoid)",
            primary_activity="Antibacterial, anti-inflammatory in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Quercetin",
            compound_class="Flavonoid",
            primary_activity="Antioxidant, anti-inflammatory",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Gedunin",
            compound_class="Terpenoid (Limonoid)",
            primary_activity="Antimalarial activity (in vitro and animal models)",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
    ],

    # ── Traditional Use ───────────────────────────────────────────────────────
    traditional_system="Ayurveda, Unani, Siddha, African traditional medicine",
    traditional_uses_summary=(
        "In Ayurveda, Neem (Nimba) has been used for skin diseases, fever, dental "
        "hygiene, wound healing, and as an anthelmintic. Neem twigs are traditionally "
        "used as toothbrushes. Neem oil is applied topically for skin conditions. "
        "Traditional use does not establish clinical efficacy."
    ),

    # ── Therapeutic Claims ────────────────────────────────────────────────────
    therapeutic_claims=[
        TherapeuticClaim(
            condition="Dental plaque and gingivitis",
            claim_text=(
                "Moderate clinical evidence supports Neem-based products for reducing "
                "dental plaque and gingivitis. Multiple small RCTs comparing Neem "
                "mouthwash/toothpaste to chlorhexidine show comparable efficacy."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            source_type="RCT",
            citation_required=True,
            citation_pmid="24882626",
            citation_flag_reason=None,
        ),
        TherapeuticClaim(
            condition="Skin conditions (acne, eczema) — topical",
            claim_text=(
                "Limited clinical evidence supports topical Neem preparations for acne "
                "vulgaris. Antimicrobial activity against Cutibacterium acnes is "
                "documented in vitro. Controlled trials are small and methodologically limited."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            source_type="In-Vitro, RCT (small scale)",
            citation_required=True,
            citation_pmid=None,
            citation_flag_reason="Need PMID for a topical skin condition RCT.",
        ),
        TherapeuticClaim(
            condition="Blood glucose regulation (oral hypoglycaemic)",
            claim_text=(
                "Animal studies demonstrate hypoglycaemic effects of Neem leaf extract. "
                "Human clinical evidence is currently insufficient — the few available "
                "trials are small and uncontrolled."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            source_type="Animal Study",
            citation_required=True,
            citation_pmid=None,
            citation_flag_reason=(
                "Seed data claims antidiabetic use without distinguishing human vs animal evidence. "
                "Needs either a human RCT PMID or reclassification to Preclinical Only."
            ),
        ),
        TherapeuticClaim(
            condition="Antimalarial activity",
            claim_text=(
                "Gedunin and other limonoids show antimalarial activity (IC50 values) "
                "in vitro against Plasmodium falciparum. Clinical efficacy in malaria "
                "treatment in humans has not been established."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            source_type="In-Vitro",
            citation_required=True,
            citation_pmid=None,
            citation_flag_reason="In-vitro data only; cannot claim clinical malaria treatment.",
        ),
        TherapeuticClaim(
            condition="Wound healing (topical)",
            claim_text=(
                "Neem leaf extract demonstrates antimicrobial and anti-inflammatory "
                "properties in animal wound models. Limited human data exists."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            source_type="Animal Study",
            citation_required=True,
            citation_pmid=None,
            citation_flag_reason="Animal model evidence only for wound healing claim.",
        ),
        TherapeuticClaim(
            condition="Blood purification",
            claim_text=(
                "The term 'blood purification' has no scientific definition. This is a "
                "traditional Ayurvedic concept (Rakta Shodhana) that cannot be translated "
                "into a clinical claim. Should not appear in evidence-based content."
            ),
            evidence_level=EvidenceLevel.NOT_SUPPORTED,
            source_type="Traditional/Ayurvedic",
            citation_required=False,
            citation_flag_reason=(
                "BANNED_PHRASE: 'blood purification'. Must be removed entirely. "
                "Replace with specific, evidence-qualified mechanisms if applicable."
            ),
        ),
    ],

    # ── Overall Evidence ──────────────────────────────────────────────────────
    overall_evidence_strength=EvidenceLevel.MODERATE_CLINICAL,
    evidence_summary=(
        "The strongest clinical evidence for Neem is in oral health — multiple "
        "RCTs support its use in dental plaque and gingivitis. Topical antimicrobial "
        "use has limited clinical backing. Systemic claims (diabetes, blood sugar, "
        "malaria) are based primarily on preclinical data and lack adequate human trials. "
        "The 'blood purification' concept has no scientific basis and should be removed."
    ),

    # ── Preparation Methods ───────────────────────────────────────────────────
    preparation_methods=[
        PreparationMethod(
            method_name="Neem Twig (Datun)",
            description="Fresh twig used as a toothbrush; chewed end applied to gums.",
            plant_part_used="Young twigs",
            intended_use="Dental hygiene — clinically studied",
            safety_note=None,
        ),
        PreparationMethod(
            method_name="Neem Leaf Decoction",
            description="Leaves boiled in water for 15 minutes; used as a skin wash or consumed.",
            plant_part_used="Leaves",
            intended_use="Traditional use for skin conditions and fever",
            safety_note=(
                "Oral consumption at high doses has caused liver enzyme elevations "
                "in case reports. Do not use in children or pregnant women."
            ),
        ),
        PreparationMethod(
            method_name="Neem Oil (topical)",
            description="Cold-pressed seed oil applied directly to affected skin areas.",
            plant_part_used="Seeds",
            intended_use="Topical use for acne, skin infections — do not ingest",
            safety_note="Not for internal use. Severe toxicity (vomiting, seizures) reported in children who ingested neem oil.",
        ),
    ],

    # ── Safety ────────────────────────────────────────────────────────────────
    safety_class=SafetyClass.CONTRAINDICATED,
    safety_warnings=[
        SafetyWarning(
            population="Infants and young children",
            warning_type="Contraindication",
            description=(
                "Neem oil ingestion in infants and young children has caused severe "
                "acute toxicity including metabolic acidosis, seizures, and deaths. "
                "Neem oil must never be given orally to children."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            citation_required=True,
            citation_pmid="11699232",
        ),
        SafetyWarning(
            population="Pregnant women",
            warning_type="Contraindication",
            description=(
                "Neem has demonstrated abortifacient properties in animal studies. "
                "Oral Neem preparations are contraindicated in pregnancy."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=True,
            citation_pmid=None,
        ),
        SafetyWarning(
            population="Patients with hepatic impairment",
            warning_type="Precaution",
            description=(
                "Case reports of Neem-induced hepatotoxicity exist. Monitor liver "
                "function tests in patients with pre-existing hepatic conditions."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmid=None,
        ),
    ],
    drug_interactions=[
        DrugInteraction(
            drug_name="Antidiabetic drugs (insulin, metformin)",
            drug_class="Antidiabetic",
            interaction_description=(
                "Additive blood glucose-lowering effect possible based on preclinical data. "
                "Clinical significance in humans not established."
            ),
            severity="Theoretical",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=True,
            citation_pmid=None,
        ),
        DrugInteraction(
            drug_name="Cyclosporine",
            drug_class="Immunosuppressant",
            interaction_description=(
                "Azadirachtin may inhibit CYP3A4 in vitro, potentially increasing "
                "cyclosporine plasma levels. Clinical significance unclear."
            ),
            severity="Theoretical",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=True,
            citation_pmid=None,
        ),
    ],
    overdose_risk=(
        "Oral ingestion of neem oil at doses exceeding 5 ml/kg has caused acute "
        "toxicity in children (metabolic acidosis, seizures, encephalopathy). "
        "High oral doses of leaf preparations may cause liver enzyme elevations. "
        "Do not use undiluted neem oil internally."
    ),

    # ── Review Metadata ───────────────────────────────────────────────────────
    review_status=ReviewStatus.FLAGGED,
    claims_requiring_citation=[
        "Skin conditions (topical acne): Needs human RCT PMID",
        "Blood glucose regulation: Animal study data — needs human RCT or reclassification",
        "Antimalarial: In-vitro only — cannot claim clinical malaria treatment",
        "Wound healing: Animal model only — needs reclassification",
        "Pregnancy contraindication: Needs pharmacological PMID for abortifacient claim",
        "Hepatotoxicity precaution: Needs case report PMID",
        "Cyclosporine interaction: Needs CYP inhibition study PMID",
    ],
    flagged_issues=[
        "CRITICAL: Seed data uses 'blood purification' — BANNED_PHRASE, must be removed entirely",
        "Seed data does not warn about infant neem oil toxicity — serious safety omission",
        "Seed data presents preclinical antidiabetic data as equivalent to clinical evidence",
        "SafetyClass should be CONTRAINDICATED (for infants/pregnancy), not USE_WITH_CAUTION",
    ],
    reviewer_notes=(
        "Neem's most dangerous data gap in the seed entry is the complete absence of "
        "the infant neem oil toxicity warning — this is a documented cause of death. "
        "This MUST be added before the app goes live. "
        "Oral health is the only indication with solid clinical backing (PMID 24882626). "
        "Remove all 'blood purification' language immediately."
    ),
    who_monograph_available=False,
    ayush_monograph_available=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# PLANT 3 — ASHWAGANDHA
# ═══════════════════════════════════════════════════════════════════════════════

ASHWAGANDHA = EvidenceBasedPlant(
    # ── Identity ──────────────────────────────────────────────────────────────
    common_name="Ashwagandha",
    local_names=["Indian Ginseng", "Winter Cherry", "Asgandh", "Vajigandha"],
    scientific_name="Withania somnifera",
    family="Solanaceae",
    description=(
        "Ashwagandha is a short perennial shrub native to the dry regions of India, "
        "North Africa, and the Mediterranean. Its roots have a horse-like smell "
        "(Sanskrit: 'ashva' = horse, 'gandha' = smell). It is one of the most important "
        "plants in Ayurvedic Rasayana (rejuvenative) medicine and is among the most "
        "clinically studied Indian medicinal plants."
    ),

    # ── Geography ─────────────────────────────────────────────────────────────
    native_region="India, North Africa, Mediterranean; naturalised in tropical regions",
    habitat="Dry stony soil, subtropical regions; cultivated in India (Madhya Pradesh, Rajasthan)",
    cultivation_status="Both",

    # ── Phytochemistry ────────────────────────────────────────────────────────
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
            primary_activity="Anticancer (apoptosis induction), anti-inflammatory",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Withanolide D",
            compound_class="Steroidal lactone (Withanolide)",
            primary_activity="Immunostimulatory, anti-tumour in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Sitoindosides VII–X",
            compound_class="Glycowithanolide",
            primary_activity="Adaptogenic, cognitive-enhancing in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
        ActiveCompound(
            compound_name="Withanine",
            compound_class="Alkaloid",
            primary_activity="Sedative, antistress in animal models",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
        ),
    ],

    # ── Traditional Use ───────────────────────────────────────────────────────
    traditional_system="Ayurveda (Rasayana / adaptogen class)",
    traditional_uses_summary=(
        "In Ayurveda, Ashwagandha root is classified as a Rasayana — a rejuvenative "
        "tonic used for debility, fatigue, sexual dysfunction, impaired memory, and "
        "as a general adaptogen. It has also been used for sleep disorders, joint pain, "
        "and as a nervine tonic. Traditional use predates clinical evidence and should "
        "not be used to imply proven therapeutic efficacy."
    ),

    # ── Therapeutic Claims ────────────────────────────────────────────────────
    therapeutic_claims=[
        TherapeuticClaim(
            condition="Stress and anxiety reduction",
            claim_text=(
                "Strong clinical evidence from multiple RCTs and a meta-analysis "
                "supports Ashwagandha root extract (KSM-66, 300–600 mg/day) for "
                "reducing perceived stress, anxiety, and serum cortisol in adults "
                "with chronic stress."
            ),
            evidence_level=EvidenceLevel.STRONG_CLINICAL,
            source_type="Meta-Analysis, RCT",
            citation_required=True,
            citation_pmid="31517876",
            citation_flag_reason=None,
        ),
        TherapeuticClaim(
            condition="Sleep quality",
            claim_text=(
                "Moderate clinical evidence supports Ashwagandha root extract for "
                "improving sleep quality and sleep onset latency in adults with "
                "insomnia, based on multiple controlled trials."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            source_type="RCT",
            citation_required=True,
            citation_pmid="32540634",
            citation_flag_reason=None,
        ),
        TherapeuticClaim(
            condition="Muscle strength and recovery (athletic performance)",
            claim_text=(
                "Moderate clinical evidence from RCTs in resistance-trained adults "
                "shows Ashwagandha supplementation improves muscle strength, muscle "
                "recovery, and VO2 max compared to placebo."
            ),
            evidence_level=EvidenceLevel.MODERATE_CLINICAL,
            source_type="RCT",
            citation_required=True,
            citation_pmid="25624699",
            citation_flag_reason=None,
        ),
        TherapeuticClaim(
            condition="Male infertility / testosterone",
            claim_text=(
                "Limited clinical evidence from small trials suggests Ashwagandha "
                "root extract may improve sperm parameters (count, motility) and "
                "testosterone levels in infertile men. Larger trials are needed."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            source_type="RCT (small scale)",
            citation_required=True,
            citation_pmid="23796876",
            citation_flag_reason=None,
        ),
        TherapeuticClaim(
            condition="Cognitive function and memory",
            claim_text=(
                "Limited clinical evidence suggests Ashwagandha may improve reaction "
                "time and cognitive task performance in healthy adults. Studies are "
                "small and short-term; effects in cognitive decline are not established."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            source_type="RCT (small scale)",
            citation_required=True,
            citation_pmid="27055824",
            citation_flag_reason=None,
        ),
        TherapeuticClaim(
            condition="Thyroid function (subclinical hypothyroidism)",
            claim_text=(
                "One small RCT reported improvements in serum TSH, T3, and T4 levels "
                "with Ashwagandha supplementation in subclinical hypothyroid patients. "
                "Replication in larger trials is required before clinical use."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            source_type="RCT (small scale)",
            citation_required=True,
            citation_pmid="28829155",
            citation_flag_reason=(
                "Thyroid stimulation is also a safety concern — may interfere with "
                "thyroid medication. Needs safety interaction note."
            ),
        ),
        TherapeuticClaim(
            condition="Anti-cancer (in vitro / preclinical)",
            claim_text=(
                "Withaferin A has demonstrated potent apoptosis-inducing activity "
                "against multiple cancer cell lines in vitro and in animal models. "
                "No clinical trials in cancer patients. This is not a clinical claim."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            source_type="In-Vitro, Animal Study",
            citation_required=True,
            citation_pmid=None,
            citation_flag_reason=(
                "Must not be presented as 'anticancer' to users. "
                "Clearly labelled as preclinical. Needs in-vitro PMID."
            ),
        ),
    ],

    # ── Overall Evidence ──────────────────────────────────────────────────────
    overall_evidence_strength=EvidenceLevel.STRONG_CLINICAL,
    evidence_summary=(
        "Ashwagandha is among the best-evidenced Indian medicinal plants. Stress/anxiety "
        "reduction has strong clinical support from multiple RCTs and a meta-analysis. "
        "Sleep quality and athletic performance have moderate evidence. Cognitive, "
        "fertility, and thyroid claims have limited clinical backing from small trials. "
        "Preclinical anticancer data must not be presented as clinical evidence. "
        "The KSM-66 and Sensoril standardised root extracts are the forms used in "
        "most clinical trials."
    ),

    # ── Preparation Methods ───────────────────────────────────────────────────
    preparation_methods=[
        PreparationMethod(
            method_name="Ashwagandha Churna (powder)",
            description="Root powder (3–6g/day) mixed with warm milk, ghee, or honey.",
            plant_part_used="Dried root",
            intended_use="Traditional adaptogenic use",
            safety_note="Avoid during pregnancy; monitor thyroid levels if on thyroid medication.",
        ),
        PreparationMethod(
            method_name="Standardised Root Extract (KSM-66)",
            description="Concentrated root extract standardised to ≥5% withanolides; 300–600 mg/day.",
            plant_part_used="Root (standardised extract)",
            intended_use="Stress, sleep, athletic performance — form used in clinical trials",
            safety_note=(
                "Consult physician if on thyroid medication, immunosuppressants, "
                "or sedatives. Avoid in pregnancy."
            ),
        ),
        PreparationMethod(
            method_name="Ashwagandha Milk (Ksheera Paka)",
            description="Root powder boiled in milk; traditional preparation for strengthening and sleep.",
            plant_part_used="Dried root",
            intended_use="Traditional use for sleep, fatigue, and debility",
            safety_note=None,
        ),
    ],

    # ── Safety ────────────────────────────────────────────────────────────────
    safety_class=SafetyClass.USE_WITH_CAUTION,
    safety_warnings=[
        SafetyWarning(
            population="Pregnant women",
            warning_type="Contraindication",
            description=(
                "Ashwagandha has documented abortifacient and uterotonic properties. "
                "Contraindicated throughout pregnancy."
            ),
            evidence_level=EvidenceLevel.TRADITIONAL_USE,
            citation_required=True,
            citation_pmid=None,
        ),
        SafetyWarning(
            population="Patients on thyroid medication (levothyroxine)",
            warning_type="Monitoring Required",
            description=(
                "Ashwagandha may increase thyroid hormone levels. Concurrent use "
                "with levothyroxine may cause hyperthyroidism. Monitor TSH levels."
            ),
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmid="28829155",
        ),
        SafetyWarning(
            population="Patients on immunosuppressants",
            warning_type="Precaution",
            description=(
                "Immunomodulatory properties of Ashwagandha may counteract "
                "immunosuppressive therapy (e.g. in transplant patients)."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=True,
            citation_pmid=None,
        ),
        SafetyWarning(
            population="Patients on CNS sedatives / benzodiazepines",
            warning_type="Precaution",
            description=(
                "Ashwagandha has sedative properties (GABA-A modulation proposed). "
                "Additive sedation with CNS depressants is possible."
            ),
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=True,
            citation_pmid=None,
        ),
        SafetyWarning(
            population="Patients with autoimmune disease (lupus, RA, MS)",
            warning_type="Advisory",
            description=(
                "Immunostimulatory effects may exacerbate autoimmune conditions. "
                "Use only under physician supervision."
            ),
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=False,
        ),
    ],
    drug_interactions=[
        DrugInteraction(
            drug_name="Levothyroxine",
            drug_class="Thyroid hormone",
            interaction_description=(
                "May increase thyroid hormone levels, risking hyperthyroid symptoms "
                "in patients already on replacement therapy."
            ),
            severity="Moderate",
            evidence_level=EvidenceLevel.LIMITED_CLINICAL,
            citation_required=True,
            citation_pmid="28829155",
        ),
        DrugInteraction(
            drug_name="Lorazepam / Diazepam",
            drug_class="Benzodiazepine (CNS depressant)",
            interaction_description=(
                "Additive sedation possible. Clinical significance uncertain "
                "but warrants caution."
            ),
            severity="Minor",
            evidence_level=EvidenceLevel.PRECLINICAL_ONLY,
            citation_required=True,
            citation_pmid=None,
        ),
        DrugInteraction(
            drug_name="Cyclosporine / Tacrolimus",
            drug_class="Immunosuppressant",
            interaction_description=(
                "Immunostimulatory properties may reduce efficacy of "
                "immunosuppressive therapy."
            ),
            severity="Theoretical",
            evidence_level=EvidenceLevel.INSUFFICIENT,
            citation_required=True,
            citation_pmid=None,
        ),
    ],
    overdose_risk=(
        "High doses (>6g root powder/day) have caused gastrointestinal distress, "
        "nausea, and diarrhoea. Case reports of liver injury at very high doses or "
        "with adulterated products exist — liver enzyme monitoring recommended for "
        "long-term high-dose use."
    ),

    # ── Review Metadata ───────────────────────────────────────────────────────
    review_status=ReviewStatus.REVIEWED,
    claims_requiring_citation=[
        "Pregnancy contraindication: Needs abortifacient pharmacological PMID",
        "Immunosuppressant interaction: Needs preclinical mechanism PMID",
        "Benzodiazepine interaction: Needs GABA-A mechanism PMID",
        "Preclinical anticancer: Needs Withaferin A in-vitro PMID",
    ],
    flagged_issues=[
        "Thyroid stimulation is both a therapeutic claim AND a safety risk — must appear in both sections",
        "Anticancer language must be explicitly marked preclinical to prevent misuse",
    ],
    reviewer_notes=(
        "Ashwagandha is the strongest plant in this dataset by clinical evidence. "
        "KSM-66 root extract (300–600 mg/day) is the evidence-supported form. "
        "Key PMIDs in hand: stress meta-analysis (31517876), sleep RCT (32540634), "
        "strength RCT (25624699), fertility (23796876), cognition (27055824), "
        "thyroid (28829155). Pregnancy and thyroid interaction are the critical safety gaps."
    ),
    who_monograph_available=False,
    ayush_monograph_available=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION — run to verify all 3 plants parse correctly
# ═══════════════════════════════════════════════════════════════════════════════

SAMPLE_PLANTS = [TULSI, NEEM, ASHWAGANDHA]

if __name__ == "__main__":
    print("=" * 70)
    print("EVIDENCE-BASED PLANT SCHEMA — SAMPLE REVIEW VALIDATION")
    print("=" * 70)

    SEP = "-" * 70
    for plant in SAMPLE_PLANTS:
        print(f"\n{SEP}")
        print(f"  {plant.common_name.upper()} ({plant.scientific_name})")
        print(SEP)
        print(f"  Family:               {plant.family}")
        print(f"  Review Status:        {plant.review_status.value}")
        print(f"  Safety Class:         {plant.safety_class.value}")
        print(f"  Overall Evidence:     {plant.overall_evidence_strength.value}")
        print(f"  Therapeutic claims:   {len(plant.therapeutic_claims)}")
        print(f"  Drug interactions:    {len(plant.drug_interactions)}")
        print(f"  Safety warnings:      {len(plant.safety_warnings)}")
        print(f"  Active compounds:     {len(plant.active_compounds)}")
        print(f"  WHO monograph:        {'Yes' if plant.who_monograph_available else 'No'}")
        print(f"  AYUSH monograph:      {'Yes' if plant.ayush_monograph_available else 'No'}")

        if plant.claims_requiring_citation:
            print(f"\n  CITATION FLAGS ({len(plant.claims_requiring_citation)}):")
            for flag in plant.claims_requiring_citation:
                print(f"    [FLAG] {flag}")

        if plant.flagged_issues:
            print(f"\n  EDITORIAL FLAGS ({len(plant.flagged_issues)}):")
            for issue in plant.flagged_issues:
                print(f"    [WARN] {issue}")

    print(f"\n{SEP}")
    print("REVIEW CHECKLIST (applies to all 20 plants)")
    print(SEP)
    for item in REVIEW_CHECKLIST:
        print(f"  [ ] {item}")

    print(f"\n{'='*70}")
    print(f"  All {len(SAMPLE_PLANTS)} plants validated successfully against schema.")
    print(f"  Total citation flags: {sum(len(p.claims_requiring_citation) for p in SAMPLE_PLANTS)}")
    print(f"  Total editorial flags: {sum(len(p.flagged_issues) for p in SAMPLE_PLANTS)}")
    print("=" * 70)
