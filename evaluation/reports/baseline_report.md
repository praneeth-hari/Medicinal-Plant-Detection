# Baseline evaluation  (2026-10-01T13:17:24)

Read-only evaluation of the saved model + FAISS index. Nothing was retrained or rebuilt.

## Classifier (MobileNetV3-Small)

| split | n | accuracy | macro-F1 |
|---|---|---|---|
| val | 999 | 93.3% | 93.0% |
| test | 1101 | 93.9% | 94.2% |
| test, backgrounds swapped | 1101 | 43.5% | 42.4% |

Mean confidence: correct 0.976, wrong 0.6894

Classes below 90% held-out accuracy: 19 / 78

Top confusions (held-out, true -> predicted):

- Amla -> Chilly: 5
- Tulsi -> Beans: 3
- Lantana -> Gasagase: 3
- Coffee -> Bringaraja: 3
- Tulsi -> Neem: 2
- Tulsi -> Bhrami: 2
- Sapota -> Mango: 2
- Nelavembu -> Catharanthus: 2
- Mint -> Tulsi: 2
- Jackfruit -> Seethapala: 2

### Per-class accuracy (worst first; held-out = val + test)

| class | train n | held-out n | held-out acc | test acc | test acc, bg swapped |
|---|---|---|---|---|---|
| Amla | 46 | 21 | 71.4% | 81.8% | 9.1% |
| Coffee | 58 | 25 | 76.0% | 69.2% | 46.2% |
| Citron lime (herelikai) | 69 | 30 | 76.7% | 87.5% | 25.0% |
| Tulsi | 123 | 54 | 77.8% | 75.0% | 57.1% |
| Lantana | 53 | 23 | 78.3% | 83.3% | 41.7% |
| Seethaashoka | 32 | 15 | 80.0% | 87.5% | 50.0% |
| Badipala | 53 | 23 | 82.6% | 91.7% | 58.3% |
| Nerale | 43 | 19 | 84.2% | 80.0% | 50.0% |
| Castor | 90 | 39 | 84.6% | 80.0% | 80.0% |
| Nelavembu | 62 | 28 | 85.7% | 80.0% | 40.0% |
| Sapota | 30 | 14 | 85.7% | 100.0% | 50.0% |
| Bamboo | 82 | 36 | 86.1% | 89.5% | 68.4% |
| Bringaraja | 51 | 22 | 86.4% | 91.7% | 25.0% |
| Malabar_Nut | 35 | 16 | 87.5% | 88.9% | 66.7% |
| Jackfruit | 77 | 33 | 87.9% | 94.1% | 58.8% |
| Aloevera | 82 | 36 | 88.9% | 89.5% | 42.1% |
| Kambajala | 41 | 18 | 88.9% | 90.0% | 40.0% |
| Lemon | 86 | 37 | 89.2% | 84.2% | 31.6% |
| Amruthaballi | 63 | 28 | 89.3% | 80.0% | 66.7% |
| Neem | 92 | 40 | 90.0% | 85.7% | 38.1% |
| Mint | 94 | 41 | 90.2% | 85.7% | 23.8% |
| Bhrami | 72 | 32 | 90.6% | 88.2% | 76.5% |
| Ganigale | 52 | 23 | 91.3% | 100.0% | 25.0% |
| Henna | 56 | 24 | 91.7% | 91.7% | 33.3% |
| Raddish | 28 | 12 | 91.7% | 100.0% | 83.3% |
| Turmeric | 27 | 12 | 91.7% | 85.7% | 28.6% |
| Ekka | 56 | 25 | 92.0% | 84.6% | 61.5% |
| Guava | 89 | 39 | 92.3% | 100.0% | 75.0% |
| Catharanthus | 93 | 41 | 92.7% | 95.2% | 28.6% |
| Jasmine | 34 | 15 | 93.3% | 100.0% | 62.5% |
| Mango | 72 | 31 | 93.5% | 87.5% | 75.0% |
| Drumstick | 39 | 17 | 94.1% | 100.0% | 0.0% |
| Coriender | 80 | 35 | 94.3% | 94.4% | 50.0% |
| Balloon_Vine | 42 | 19 | 94.7% | 100.0% | 50.0% |
| Sampige | 42 | 19 | 94.7% | 100.0% | 40.0% |
| Spinach1 | 46 | 21 | 95.2% | 100.0% | 63.6% |
| kamakasturi | 46 | 21 | 95.2% | 90.9% | 9.1% |
| Padri | 51 | 22 | 95.5% | 91.7% | 91.7% |
| Palak(Spinach) | 104 | 45 | 95.6% | 95.7% | 52.2% |
| Pomoegranate | 52 | 23 | 95.7% | 100.0% | 8.3% |
| Gasagase | 55 | 24 | 95.8% | 92.3% | 84.6% |
| Malabar_Spinach | 55 | 24 | 95.8% | 92.3% | 92.3% |
| Astma_weed | 57 | 25 | 96.0% | 92.3% | 7.7% |
| Curry | 117 | 51 | 96.1% | 96.2% | 23.1% |
| Pumpkin | 64 | 28 | 96.4% | 93.3% | 60.0% |
| Rose | 74 | 32 | 96.9% | 94.1% | 0.0% |
| Honge | 79 | 34 | 97.1% | 100.0% | 33.3% |
| Hibiscus | 82 | 36 | 97.2% | 100.0% | 5.3% |
| Doddpathre | 99 | 43 | 97.7% | 100.0% | 45.5% |
| Arali | 62 | 27 | 100.0% | 100.0% | 85.7% |
| Beans | 67 | 30 | 100.0% | 100.0% | 37.5% |
| Betel | 79 | 35 | 100.0% | 100.0% | 61.1% |
| Caricature | 53 | 23 | 100.0% | 100.0% | 33.3% |
| Chakte | 47 | 21 | 100.0% | 100.0% | 72.7% |
| Chilly | 48 | 21 | 100.0% | 100.0% | 0.0% |
| Common rue(naagdalli) | 46 | 21 | 100.0% | 100.0% | 72.7% |
| Eucalyptus | 56 | 24 | 100.0% | 100.0% | 41.7% |
| Ganike | 44 | 19 | 100.0% | 100.0% | 30.0% |
| Ginger | 57 | 25 | 100.0% | 100.0% | 15.4% |
| Globe Amarnath | 56 | 25 | 100.0% | 100.0% | 23.1% |
| Insulin | 62 | 27 | 100.0% | 100.0% | 50.0% |
| Kasambruga | 33 | 15 | 100.0% | 100.0% | 37.5% |
| Kohlrabi | 51 | 22 | 100.0% | 100.0% | 58.3% |
| Marigold | 65 | 28 | 100.0% | 100.0% | 13.3% |
| Nooni | 50 | 22 | 100.0% | 100.0% | 75.0% |
| Onion | 64 | 28 | 100.0% | 100.0% | 33.3% |
| Papaya | 94 | 41 | 100.0% | 100.0% | 85.7% |
| Parijatha | 46 | 20 | 100.0% | 100.0% | 36.4% |
| Pea | 32 | 15 | 100.0% | 100.0% | 25.0% |
| Seethapala | 79 | 35 | 100.0% | 100.0% | 33.3% |
| Tamarind | 123 | 53 | 100.0% | 100.0% | 7.4% |
| Taro | 48 | 21 | 100.0% | 100.0% | 72.7% |
| Tecoma | 48 | 21 | 100.0% | 100.0% | 9.1% |
| Thumbe | 51 | 23 | 100.0% | 100.0% | 8.3% |
| Tomato | 43 | 19 | 100.0% | 100.0% | 0.0% |
| ashoka | 56 | 25 | 100.0% | 100.0% | 30.8% |
| camphor | 46 | 20 | 100.0% | 100.0% | 72.7% |
| kepala | 53 | 23 | 100.0% | 100.0% | 33.3% |

RAG knowledge-base coverage of classifier classes: **13 / 78**

## Duplicate / leakage audit

Images scanned: 6884

- Exact duplicate groups: 41 (across splits: 20, across classes: 0)
- val vs train (64-bit dHash): identical 2.2%, near (<=4 bits) 10.4%, similar (<=8 bits) 25.8%, median nearest distance 12.0
- test vs train (64-bit dHash): identical 1.6%, near (<=4 bits) 9.2%, similar (<=8 bits) 22.4%, median nearest distance 12.0
- test vs val near (<=4 bits): 3.3%
- Test accuracy WITH a near-duplicate in train: 96.8% (n=247); WITHOUT: 93.1% (n=854)
- timestamped_filenames_heldout_vs_train_same_class: {'n_heldout': 578, 'pct_within_60s': 0.9689, 'pct_within_1h': 1.0, 'pct_same_day': 1.0}
- sequential_filenames_heldout_vs_train_same_class: {'n_heldout': 1272, 'pct_adjacent_le1': 0.0, 'pct_within_3': 0.9072}
- Filename patterns: [('N.jpg', 4173), ('img_N_N.jpg', 1404), ('N_N.jpg', 789), ('p_N_N.jpg', 378), ('p_N_N_vhdr_on.jpg', 34), ('img_N_N__N.jpg', 31)]

## RAG retrieval

40 questions, 40 chunks, 20 plants in the index. Question categories: {'therapeutic_uses': 19, 'safety_precautions': 14, 'misconceptions': 5, 'preparation': 2}

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
