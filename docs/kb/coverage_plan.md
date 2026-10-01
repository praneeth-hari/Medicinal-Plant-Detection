# Knowledge-base coverage plan

Status: **plan for review. No production RAG code, index or knowledge-base content was changed.**
Machine-readable version of all 78 classes: [coverage_plan.csv](coverage_plan.csv).

## 0. How to read this plan

- Per-plant citations (specific monograph pages, PMIDs, IMPPAT/PubChem entries) could not be verified from here, and the brief was not to fill gaps from model knowledge. So this plan fixes the **source stack, lookup keys and rules**; the per-plant references get collected during the authoring step, each one fetched and recorded.
- Scientific names come from the dataset's own species table (DIMPSAR, Mendeley DOI 10.17632/748f8jkphb.3; table read from the [PMC paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10375553/)), not from memory. Where that table is silent or ambiguous it is flagged below.
- WHO monograph availability is now checked against the cumulative index (Annex 2, pp. 395-396) of WHO monographs Volume 4, which lists the monographs of Volumes 1-4. It was read from a third-party scan of the PDF because WHO's own server returned 403, so it is still worth a check against the official copy. Plant-material scope matters: a monograph on one part (for example castor *oil*) does not cover other parts, and species must match.

## 1. The 78 detectable plants

- 78 class folders = the dataset's 80 species minus Pepper and Lemongrass (18 photos each, below the 30-photo minimum in `ml/prepare_dataset.py`).
- **13 covered** by the current KB:

- Aloevera (Aloe barbadensis miller) - confirmed
- Amla (Phyllanthus emblica) - confirmed
- Amruthaballi (Tinospora cordifolia) - confirmed
- Bhrami (Bacopa monnieri) - confirmed
- Bringaraja (Eclipta prostrate [sic: prostrata]) - confirmed
- Curry (Murraya koenigii) - confirmed
- Drumstick (Moringa oleifera) - confirmed
- Ginger (Zingiber officinale) - confirmed
- Hibiscus (Hibiscus rosa-sinensis) - confirmed
- Mint (Mentha) - genus-level only
- Neem (Azadirachta indica) - confirmed
- Tulsi (Ocimum tenuiflorum) - confirmed
- Turmeric (Curcuma longa) - confirmed

- **65 missing.** Identity status of the 65: **48 confirmed, 3 needs source verification, 6 genus-level only, 8 unresolved.** `Palak(Spinach)` and `Spinach1` are the same species, so one KB entry serves both.
- 7 plants are in the KB but the classifier cannot detect them: Ashwagandha, Garlic, Lemongrass, Shatavari, Arjuna, Bael, Fenugreek. They stay, but are not part of this plan.
- Authoring is gated by identity status: content is written only for `confirmed` plants. `genus-level only` plants get a genus-level entry with no species-specific claims. `needs source verification` and `unresolved` plants get no therapeutic, phytochemical, preparation or safety content until resolved.

## 2. Identity resolution report

How the evidence was gathered (in order of weight):
1. **The DIMPSAR paper's species table** ([PMC10375553](https://pmc.ncbi.nlm.nih.gov/articles/PMC10375553/), Data in Brief DOI 10.1016/j.dib.2023.109388). It has exactly 80 rows. It gives no footnotes, no supplementary tables and no folder-naming convention. Its only provenance statement is that the species list came "with the help of botanists, phytochemists and data sources", with no per-species verification.
2. **The Mendeley dataset page** (DOI 10.17632/748f8jkphb.3): description only. It exposes no file list or name sheet to me.
3. **Sample-count cross-check (new).** The paper gives a sample count per species. I counted the files in each local `data/raw` folder: **75 of 78 folders match the paper's count for the row I paired them with**; the 3 exceptions are Kambajala (59 vs 60), Spinach1 (70 vs 54) and Tamarind (176 vs 156). Where a count is unique this strongly supports the folder<->row link. Where several rows share a count it cannot discriminate. A matching count links a folder to a row; it does not prove the row's botanical name is right.
4. **Independent vernacular-name sources** (eFloraofIndia, WisdomLib, recipe and botany blogs). Corroborating only; not treated as authoritative.
5. **Sample images**, viewed by me. Used only to detect contradictions, never to assign a species.

Searches of other dataset papers (including the Tamil Nadu SIMPD dataset) and a third-party Roboflow derivative found no usable species table for the unresolved names. Several pages could not be fetched (403/404), including the WHO volume PDFs, the ScienceDirect article and the Roboflow page.

### Resolved / unresolved by question

**1. The four blank botanical names: all four stay UNRESOLVED.** Badipala, Chakte, Seethaashoka, Kasambruga. The paper prints no botanical name and explains nothing. No other source was found. The folder-to-row link is sound for Chakte and Kasambruga (unique counts), but the species is unknown.

**2. The four inferred mappings:**

| Folder | Status | Why |
|---|---|---|
| Ekka | **UNRESOLVED** | Elimination only; count 81 is shared by three rows, so it cannot discriminate. |
| Ganike | needs source verification | Unique count match with row 57 (Black nightshade, *Solanum nigrum*), plus independent sources that Kannada "Ganike soppu" is *Solanum nigrum*. No authoritative confirmation. |
| Kambajala | **UNRESOLVED** | Count differs (59 vs 60), and the sample images show two-lobed simple leaves, which do not fit Butterfly pea (*Clitoria ternatea*, compound leaves). The pairing now looks wrong, not just unverified. |
| kepala | needs source verification | Residual of a four-way shared count, plus independent sources that Kannada "Kepala" is *Ixora coccinea*. Needs confirmation. |

**3. The duplicate *Calotropis gigantea* (Aak and Ganigale):** the paper has no note on it. The two folders hold visibly different leaves (Ekka: broad, pale, ovate; Ganigale: long, narrow, lanceolate), so they cannot be the same species. **The name printed for Ganigale is therefore very likely wrong**, and its real species is unknown (UNRESOLVED). Ekka remains unresolved as well, so *Calotropis gigantea* currently has **no confirmed class folder**. I did not pick either. The image comparison is my visual observation, not an authoritative identification.

**4. Genus-level classes:** the dataset provides **no species-level identification** for Bamboo (only the subfamily *Bambusoideae*), Beans (*Phaseolus*), Coffee (*Coffea*), Jasmine (*Jasminum*), Pea (*Pisum*), Rose (*Rosa*) and Mint (*Mentha*). I found nothing elsewhere to narrow them. No species was invented. Consequence for Mint: the KB and the `plants` table say *Mentha spicata*, which the dataset does not support.

### Two further problems found along the way (not in your list)

- **Pumpkin: UNRESOLVED.** The table pairs the common name "Fluted pumpkin leaf" with *Cucurbita moschata*, but fluted pumpkin is *Telfairia occidentalis*, a different species. The dataset contradicts itself.
- **Ashoka: needs source verification.** The paper says *Saraca asoca*, but every sampled image shows a simple lanceolate leaf with a distinctly wavy margin. *Saraca asoca* has compound paripinnate leaves, and *Polyalthia longifolia* ("false ashoka") has simple wavy lanceolate leaves and is a documented bark adulterant. This could be a misidentification or just my reading of single leaflets; a botanist should check. It matters because the two plants have different safety data.

### What this means for the plan

- The authoring-ready (confirmed) set is **48 of 65**. The planned pilot (Guava, Castor, Tomato) is unaffected: all three are confirmed, with unique or name-resolved counts.
- The WHO candidate column still applies only to confirmed plants. Pumpkin's WHO candidate (Semen Cucurbitae) is moot while its identity is unresolved.
- **Recommended escalation:** the 4 blank names, Ekka, Ganigale, Kambajala and Pumpkin cannot be resolved from public documents. Options: (a) contact the dataset's corresponding author through the Data in Brief paper for the original name sheet, or (b) have a botanist identify the species from the sample images. Both are outside what I can do. I can draft the author email.

### Registry alignment (plants table as canonical)

The `plants` table is live: [detection_service.py](../../backend/services/detection_service.py) resolves classifier labels to `plants` rows by case-insensitive `common_name`, and the plant API reads from it. Today the name mapping is spread over **four separate lists** that can drift apart:

| List | Where | Size |
|---|---|---|
| Classifier labels | `class_mapping.json` | 78 |
| Folder-to-DB aliases | `_ALIAS_MAP` in `ml/predict.py` | 7 entries; everything else is title-cased, so a typo'd folder like `Pomoegranate` would silently fail to match a DB row |
| Retriever plant names | hardcoded list in `rag/retriever.py` | 20 |
| KB chunk metadata plant names | `build_index.py` | 20 |

The `plants` table has `common_name`, `scientific_name` and `local_names` but **no field that links a classifier label to a row**. Proposed alignment (not implemented): add one nullable, unique `class_label` column to `plants`, set from the confirmed rows of this plan, then derive the aliases, the retriever's name matching and the RAG chunk metadata (`plant_id`) from that table. That replaces the three hand-kept lists with one source of truth, and plants with unresolved identity simply get no row. Adding rows for only the confirmed plants keeps unresolved identities out of the registry.

## 3. Source stack (applies to every missing plant)

Priority runs top to bottom within each field. A field with no qualifying source is stored as `not_available`, and **no chunk is generated for it**. The assistant then correctly says the monographs don't cover it.

| Field | Primary sources | Fallback / cross-check | Lookup key |
|---|---|---|---|
| **Identity and taxonomy** | [Plants of the World Online (Kew)](https://powo.science.kew.org) for accepted name, synonyms, family, native range | Flora of India / Indian Biodiversity Portal; the dataset table | scientific name |
| **Basic description** | Pharmacopoeial monographs (WHO "description" sections; Ayurvedic Pharmacopoeia of India) | Flora of India | accepted scientific name |
| **Traditional and medicinal uses** | WHO Monographs (Vol 1-4) "uses described in traditional medicine" section; Ayurvedic Pharmacopoeia of India and AYUSH monographs; EMA/HMPC monographs where one exists | Peer-reviewed ethnobotany reviews on PubMed. Each use is tagged `traditional` vs `clinical`. | scientific name plus Sanskrit/Kannada name |
| **Phytochemistry** | [IMPPAT 2.0](https://cb.imsc.res.in/imppat/) (4,010 Indian plants, 17,967 phytochemicals, from 100+ traditional texts); compound identity via [PubChem](https://pubchem.ncbi.nlm.nih.gov) | WHO monograph "chemical constituents" sections; PubMed reviews | scientific name; compound name/CID |
| **Safety and precautions** | WHO monographs (contraindications, warnings, adverse reactions); EMA/HMPC; NCCIH where a page exists; NIH [LiverTox](https://www.ncbi.nlm.nih.gov/books/NBK547852/) for liver-injury reports | PubMed case reports and systematic reviews, tagged with study type | scientific name |
| **Regulatory status** | CDSCO / AYUSH (India); for controlled species, the national law itself | - | species |
| **References** | Every claim carries a `source_id` that resolves to a registry entry (title, publisher, year, URL/DOI/PMID, access date) | - | - |

Rules that go with the stack:
- **Two-source rule for safety.** Any contraindication or interaction needs a source that states it. If only a trade or blog source supports it, it is dropped, not softened.
- **No inference across species.** WHO data for *Cucurbita pepo* cannot be used for *C. moschata* unless the monograph covers both.
- **Food and ornamental plants** (e.g. Tomato, Beans, Pea, Kohlrabi, Rose, Marigold) will often have no monograph. They get a minimal entry (identity, edible/ornamental use where sourced, safety if any) and an explicit `evidence: insufficient` flag, not invented therapeutic text.
- **Hazard triage first.** Before any therapeutic text, plants that are potentially toxic or legally controlled need toxicology/legal sources and a mandatory safety chunk. From general knowledge (to be verified, not KB content), the ones to review first are: Gasagase (*Papaver somniferum*, likely controlled), Castor, Ekka/Ganigale (*Calotropis*), Catharanthus, Common rue, Lantana, Ganike (*Solanum nigrum*), Tecoma and Astma_weed.

## 4. Proposed schema

The repo already has the right foundation: [evidence_schema.py](../../backend/schemas/evidence_schema.py) (`EvidenceBasedPlant`) with evidence levels, PMIDs, review status and WHO/AYUSH flags, five fully authored pilot plants, and `PlantValidator` with 15 rules. I propose **no new schema**: author each plant as an `EvidenceBasedPlant`, validate it, and **render chunks from it automatically**. That avoids hand-written text drifting from the structured record.

**Pipeline:** source record (JSON, one per plant) -> `PlantValidator` -> chunk renderer -> `build_index.py`.

**Chunk rules (one chunk per section, never cut mid-section):**

| `section` | Content | Matches eval category |
|---|---|---|
| `identity` | accepted name, family, local names, description, native range, plant part used | - |
| `traditional_use` | traditional uses, each tagged with system (Ayurveda/Siddha/Unani) | therapeutic_uses |
| `phytochemistry` | main constituents with source | - |
| `evidence` | what clinical evidence exists, or "insufficient" | therapeutic_uses |
| `preparation` | preparation methods and dosage where sourced | preparation |
| `safety` | contraindications, pregnancy, interactions, overdose | safety_precautions |
| `misconceptions` | only where a source documents the myth | misconceptions |

Each chunk text starts with a fixed header, e.g. `Plant: Tulsi (Ocimum tenuiflorum) | Section: safety`, so the embedding always knows the plant and topic. This also targets the retrieval weakness measured in the baseline (safety questions hit at rank 1 only 57% of the time, because precautions share chunks with other text).

**Chunk metadata (identical for every chunk):**

```json
{
  "plant_id": "ocimum-tenuiflorum",
  "common_name": "Tulsi",
  "scientific_name": "Ocimum tenuiflorum",
  "class_folder": "Tulsi",
  "aliases": ["Holy Basil", "Tulasi"],
  "section": "safety",
  "category": "safety_precautions",
  "evidence_level": "insufficient | traditional | limited | moderate | strong",
  "source_ids": ["who-v2-ocimi-sancti", "pmid-12345678"],
  "who_monograph": true,
  "review_status": "pending | reviewed",
  "last_reviewed": "YYYY-MM-DD",
  "kb_version": "2026.10",
  "chunk_index": 3,
  "total_chunks": 6
}
```

(The values above are format examples only, not content.) A separate `sources.json` registry holds the full citation for every `source_id`. The retriever can later filter on `plant_id`, `section` and `evidence_level`. The `aliases` and `class_folder` fields replace the hardcoded plant-name list in `retriever.py`, which is the second half of the coverage fix.

## 5. Proposed order of work (for your approval)

1. **Identity gate (this report).** Escalate the unresolved set to the dataset authors or a botanist in parallel with everything else.
2. **Pilot of 3 confirmed plants end to end:** Guava (WHO candidate), Castor (WHO candidate, hazard-triage) and Tomato (food plant, thin evidence). All three are confirmed.
3. **Remaining confirmed plants with WHO candidates:** Onion, Eucalyptus, Nelavembu, Pomegranate. Eucalyptus still needs the species check against *E. globulus*.
4. **Hazard-triage and other confirmed plants** in batches of about 10, validated with `PlantValidator`.
5. **Genus-level plants** with explicit genus-level wording; **needs-verification and unresolved plants** only after their identity is settled.
6. **Registry alignment** (`class_label` on `plants`, derive the other lists) before the first KB build that includes the new plants.
7. **Expand `evaluation_dataset.json`** alongside, including questions that do not name the plant and questions where the right answer is "no information".
