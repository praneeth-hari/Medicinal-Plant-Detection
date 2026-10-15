# Sample Image Attributions

The three leaf images in this directory (`neem.jpg`, `giloy.jpg`, `aloe_vera.jpg`)
are used as one-click demo samples on the Plant Detection page.

## Source

- **Dataset:** Indian Medicinal Leaves Image Datasets
- **Authors:** Pushpa B R; Rani, Shobha
- **Version:** 3
- **Published:** 5 May 2023
- **Publisher:** Mendeley Data
- **DOI / Source URL:** https://doi.org/10.17632/748f8jkphb.3
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **License URL:** http://creativecommons.org/licenses/by/4.0

## Files and originals

| File in this directory | Original path in dataset | Class label |
|---|---|---|
| `neem.jpg` | `Neem/1084.jpg` | Neem |
| `giloy.jpg` | `Amruthaballi/538.jpg` | Amruthaballi (Giloy) |
| `aloe_vera.jpg` | `Aloevera/152.jpg` | Aloevera (Aloe Vera) |

Images were copied without modification (pixel content unchanged).

## Required attribution (CC BY 4.0 Section 3(a)(1))

Pushpa B R; Rani, Shobha (2023).
Indian Medicinal Leaves Image Datasets (Version 3) [Data set].
Mendeley Data. https://doi.org/10.17632/748f8jkphb.3
License: CC BY 4.0

## Provenance note

The local dataset (data/raw/, git-ignored) was split into data/train/,
data/val/, and data/test/ by ml/prepare_dataset.py at a 70/15/15 ratio
with random.seed(42). The sample images above are drawn from data/val/.

The link between the local files and the Mendeley dataset is established by:
- Class folder names matching the Mendeley v3 description exactly (78 classes).
- backend/data/dataset_inventory_report.csv listing the same class set.
- data/README.md directing users to download or link the raw dataset locally.

No explicit DATASET_SOURCE record exists in the repository. The provenance
chain is strong but inferred, not documented inline. A future commit should
add a DATASET_SOURCE.md at the repo root citing the DOI directly.
