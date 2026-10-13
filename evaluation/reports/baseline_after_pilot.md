# Baseline evaluation  (2026-10-01T17:46:45)

Read-only evaluation of the saved model + FAISS index. Nothing was retrained or rebuilt.

## Classifier (MobileNetV3-Small)

| split | n | accuracy | macro-F1 |
|---|---|---|---|
| val | 999 | 85.5% | 86.0% |
| test | 1101 | 82.5% | 83.3% |
| test, backgrounds swapped | 1101 | 70.6% | 70.8% |

Mean confidence: correct 0.9187, wrong 0.6246

Classes below 90% held-out accuracy: 49 / 78

Top confusions (held-out, true -> predicted):

- Castor -> Papaya: 14
- Marigold -> Neem: 8
- Honge -> Parijatha: 7
- Chilly -> Tomato: 5
- Badipala -> Guava: 5
- Tulsi -> Lemon: 4
- Tamarind -> Neem: 4
- Seethaashoka -> Nerale: 4
- Hibiscus -> Parijatha: 4
- Common rue(naagdalli) -> Papaya: 4

### Per-class accuracy (worst first; held-out = val + test)

| class | train n | held-out n | held-out acc | test acc | test acc, bg swapped |
|---|---|---|---|---|---|
| Seethaashoka | 32 | 15 | 40.0% | 50.0% | 25.0% |
| Chilly | 48 | 21 | 42.9% | 36.4% | 27.3% |
| Marigold | 65 | 28 | 50.0% | 46.7% | 33.3% |
| Tulsi | 123 | 54 | 50.0% | 35.7% | 42.9% |
| Amla | 46 | 21 | 57.1% | 54.5% | 27.3% |
| Castor | 90 | 39 | 59.0% | 50.0% | 60.0% |
| Balloon_Vine | 42 | 19 | 63.2% | 70.0% | 50.0% |
| Badipala | 53 | 23 | 65.2% | 58.3% | 33.3% |
| Honge | 79 | 34 | 67.7% | 66.7% | 61.1% |
| Sampige | 42 | 19 | 68.4% | 80.0% | 70.0% |
| Citron lime (herelikai) | 69 | 30 | 70.0% | 56.2% | 43.8% |
| Common rue(naagdalli) | 46 | 21 | 71.4% | 54.5% | 27.3% |
| Hibiscus | 82 | 36 | 72.2% | 79.0% | 73.7% |
| Catharanthus | 93 | 41 | 73.2% | 66.7% | 61.9% |
| Coffee | 58 | 25 | 76.0% | 53.8% | 61.5% |
| Sapota | 30 | 14 | 78.6% | 87.5% | 62.5% |
| Betel | 79 | 35 | 80.0% | 77.8% | 66.7% |
| Aloevera | 82 | 36 | 80.6% | 79.0% | 73.7% |
| Spinach1 | 46 | 21 | 81.0% | 72.7% | 81.8% |
| kamakasturi | 46 | 21 | 81.0% | 81.8% | 45.5% |
| Lemon | 86 | 37 | 81.1% | 89.5% | 79.0% |
| Malabar_Nut | 35 | 16 | 81.2% | 77.8% | 55.6% |
| Doddpathre | 99 | 43 | 81.4% | 86.4% | 54.5% |
| Padri | 51 | 22 | 81.8% | 83.3% | 91.7% |
| Seethapala | 79 | 35 | 82.9% | 94.4% | 66.7% |
| Kambajala | 41 | 18 | 83.3% | 90.0% | 80.0% |
| Mango | 72 | 31 | 83.9% | 81.2% | 56.2% |
| Ekka | 56 | 25 | 84.0% | 69.2% | 61.5% |
| Ganike | 44 | 19 | 84.2% | 80.0% | 70.0% |
| Tomato | 43 | 19 | 84.2% | 90.0% | 60.0% |
| Bhrami | 72 | 32 | 84.4% | 82.3% | 94.1% |
| Jackfruit | 77 | 33 | 84.9% | 94.1% | 76.5% |
| Insulin | 62 | 27 | 85.2% | 78.6% | 78.6% |
| Mint | 94 | 41 | 85.4% | 76.2% | 76.2% |
| Chakte | 47 | 21 | 85.7% | 100.0% | 100.0% |
| Taro | 48 | 21 | 85.7% | 72.7% | 63.6% |
| Bringaraja | 51 | 22 | 86.4% | 83.3% | 50.0% |
| Nooni | 50 | 22 | 86.4% | 83.3% | 83.3% |
| Jasmine | 34 | 15 | 86.7% | 100.0% | 87.5% |
| Caricature | 53 | 23 | 87.0% | 75.0% | 66.7% |
| Pomoegranate | 52 | 23 | 87.0% | 83.3% | 75.0% |
| kepala | 53 | 23 | 87.0% | 75.0% | 41.7% |
| Astma_weed | 57 | 25 | 88.0% | 84.6% | 69.2% |
| Drumstick | 39 | 17 | 88.2% | 77.8% | 55.6% |
| Coriender | 80 | 35 | 88.6% | 88.9% | 88.9% |
| Bamboo | 82 | 36 | 88.9% | 89.5% | 73.7% |
| Nelavembu | 62 | 28 | 89.3% | 86.7% | 80.0% |
| Nerale | 43 | 19 | 89.5% | 80.0% | 80.0% |
| Guava | 89 | 39 | 89.7% | 100.0% | 85.0% |
| Beans | 67 | 30 | 90.0% | 93.8% | 68.8% |
| Neem | 92 | 40 | 90.0% | 85.7% | 90.5% |
| Tecoma | 48 | 21 | 90.5% | 90.9% | 18.2% |
| Tamarind | 123 | 53 | 90.6% | 92.6% | 81.5% |
| Lantana | 53 | 23 | 91.3% | 83.3% | 75.0% |
| Eucalyptus | 56 | 24 | 91.7% | 83.3% | 66.7% |
| Gasagase | 55 | 24 | 91.7% | 92.3% | 84.6% |
| Henna | 56 | 24 | 91.7% | 91.7% | 66.7% |
| Raddish | 28 | 12 | 91.7% | 100.0% | 83.3% |
| Ginger | 57 | 25 | 92.0% | 92.3% | 61.5% |
| Globe Amarnath | 56 | 25 | 92.0% | 92.3% | 69.2% |
| Kasambruga | 33 | 15 | 93.3% | 87.5% | 75.0% |
| Rose | 74 | 32 | 93.8% | 88.2% | 64.7% |
| camphor | 46 | 20 | 95.0% | 100.0% | 100.0% |
| Palak(Spinach) | 104 | 45 | 95.6% | 100.0% | 95.7% |
| Ganigale | 52 | 23 | 95.7% | 91.7% | 75.0% |
| Thumbe | 51 | 23 | 95.7% | 91.7% | 50.0% |
| Malabar_Spinach | 55 | 24 | 95.8% | 100.0% | 92.3% |
| ashoka | 56 | 25 | 96.0% | 92.3% | 76.9% |
| Curry | 117 | 51 | 96.1% | 100.0% | 92.3% |
| Amruthaballi | 63 | 28 | 96.4% | 93.3% | 80.0% |
| Onion | 64 | 28 | 96.4% | 100.0% | 93.3% |
| Arali | 62 | 27 | 100.0% | 100.0% | 92.9% |
| Kohlrabi | 51 | 22 | 100.0% | 100.0% | 75.0% |
| Papaya | 94 | 41 | 100.0% | 100.0% | 100.0% |
| Parijatha | 46 | 20 | 100.0% | 100.0% | 100.0% |
| Pea | 32 | 15 | 100.0% | 100.0% | 100.0% |
| Pumpkin | 64 | 28 | 100.0% | 100.0% | 86.7% |
| Turmeric | 27 | 12 | 100.0% | 100.0% | 85.7% |

RAG knowledge-base coverage of classifier classes: **16 / 78**

## Duplicate / leakage audit

Images scanned: 6884

- Exact duplicate groups: 41 (across splits: 20, across classes: 0)
- val vs train (64-bit dHash): identical 2.2%, near (<=4 bits) 10.4%, similar (<=8 bits) 25.8%, median nearest distance 12.0
- test vs train (64-bit dHash): identical 1.6%, near (<=4 bits) 9.2%, similar (<=8 bits) 22.4%, median nearest distance 12.0
- test vs val near (<=4 bits): 3.3%
- Test accuracy WITH a near-duplicate in train: 82.6% (n=247); WITHOUT: 82.4% (n=854)
- timestamped_filenames_heldout_vs_train_same_class: {'n_heldout': 578, 'pct_within_60s': 0.9689, 'pct_within_1h': 1.0, 'pct_same_day': 1.0}
- sequential_filenames_heldout_vs_train_same_class: {'n_heldout': 1272, 'pct_adjacent_le1': 0.0, 'pct_within_3': 0.9072}
- Filename patterns: [('N.jpg', 4173), ('img_N_N.jpg', 1404), ('N_N.jpg', 789), ('p_N_N.jpg', 378), ('p_N_N_vhdr_on.jpg', 34), ('img_N_N__N.jpg', 31)]

## RAG retrieval

40 questions, 78 chunks, 23 plants in the index. Question categories: {'therapeutic_uses': 19, 'safety_precautions': 14, 'misconceptions': 5, 'preparation': 2}

`plant` = a top-k chunk comes from the expected plant. `plant+category` = a top-k chunk from the expected plant that contains the expected section (Medicinal Uses / Preparation / Precautions / Misconceptions).

| pipeline | match | Hit@1 | Hit@3 | Hit@5 |
|---|---|---|---|---|
| production_retriever | plant | 100.0% | 100.0% | 100.0% |
| production_retriever | plant+category | 82.5% | 100.0% | 100.0% |
| raw_faiss | plant | 100.0% | 100.0% | 100.0% |
| raw_faiss | plant+category | 82.5% | 100.0% | 100.0% |

### production_retriever: plant+category by question category

| category | n | Hit@1 | Hit@3 | Hit@5 |
|---|---|---|---|---|
| misconceptions | 5 | 100.0% | 100.0% | 100.0% |
| preparation | 2 | 100.0% | 100.0% | 100.0% |
| safety_precautions | 14 | 57.1% | 100.0% | 100.0% |
| therapeutic_uses | 19 | 94.7% | 100.0% | 100.0% |

Top-1 from the wrong plant: 0 / 40
Questions with no plant+category hit in top 5: 0

### raw_faiss: plant+category by question category

| category | n | Hit@1 | Hit@3 | Hit@5 |
|---|---|---|---|---|
| misconceptions | 5 | 100.0% | 100.0% | 100.0% |
| preparation | 2 | 100.0% | 100.0% | 100.0% |
| safety_precautions | 14 | 57.1% | 100.0% | 100.0% |
| therapeutic_uses | 19 | 94.7% | 100.0% | 100.0% |

Top-1 from the wrong plant: 0 / 40
Questions with no plant+category hit in top 5: 0
