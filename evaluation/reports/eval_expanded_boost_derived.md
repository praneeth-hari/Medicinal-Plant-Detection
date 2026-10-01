# Baseline evaluation  (2026-10-01T18:35:22)

Read-only evaluation of the saved model + FAISS index. Nothing was retrained or rebuilt.

## RAG retrieval

89 questions, 78 chunks, 23 plants in the index. Question categories: {'therapeutic_uses': 30, 'safety_precautions': 33, 'misconceptions': 5, 'preparation': 6, 'identity': 9, 'phytochemistry': 6}

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

Top-1 from the wrong plant: 0 / 89
Questions with no plant+category hit in top 5: 0

### raw_faiss: plant+category by question category

| category | n | Hit@1 | Hit@3 | Hit@5 |
|---|---|---|---|---|
| misconceptions | 5 | 100.0% | 100.0% | 100.0% |
| preparation | 2 | 100.0% | 100.0% | 100.0% |
| safety_precautions | 14 | 57.1% | 100.0% | 100.0% |
| therapeutic_uses | 19 | 94.7% | 100.0% | 100.0% |

Top-1 from the wrong plant: 0 / 89
Questions with no plant+category hit in top 5: 0

## RAG retrieval by question set

40 original questions + 49 pilot questions, 78 chunks. 'answer-chunk' = the chunk of the right plant and category that contains the phrases the answer needs (pilot questions only).

### production_retriever

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| original | 40 | 100.0% | 82.5% | 100.0% | 100.0% | - | 0 |
| pilot | 49 | 100.0% | 79.6% | 100.0% | 100.0% | 77.5% / 93.9% / 95.9% (n=49) | 0 |
| combined | 89 | 100.0% | 80.9% | 100.0% | 100.0% | 77.5% / 93.9% / 95.9% (n=49) | 0 |

production_retriever / original: by category

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| misconceptions | 5 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| preparation | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| safety_precautions | 14 | 100.0% | 57.1% | 100.0% | 100.0% | - | 0 |
| therapeutic_uses | 19 | 100.0% | 94.7% | 100.0% | 100.0% | - | 0 |

production_retriever / original: by plant

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| Aloe Vera | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Amla | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Arjuna | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Ashwagandha | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Bael | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Bhringraj | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Brahmi | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Curry Leaves | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Fenugreek | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Garlic | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Giloy | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Ginger | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Hibiscus | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Lemongrass | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Mint | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Moringa | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Neem | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Shatavari | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Tulsi | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Turmeric | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |

production_retriever / pilot: by category

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| identity | 9 | 100.0% | 77.8% | 100.0% | 100.0% | 77.8% / 100.0% / 100.0% (n=9) | 0 |
| phytochemistry | 6 | 100.0% | 83.3% | 100.0% | 100.0% | 83.3% / 100.0% / 100.0% (n=6) | 0 |
| preparation | 4 | 100.0% | 75.0% | 100.0% | 100.0% | 75.0% / 100.0% / 100.0% (n=4) | 0 |
| safety_precautions | 19 | 100.0% | 79.0% | 100.0% | 100.0% | 79.0% / 94.7% / 100.0% (n=19) | 0 |
| therapeutic_uses | 11 | 100.0% | 81.8% | 100.0% | 100.0% | 72.7% / 81.8% / 81.8% (n=11) | 0 |

production_retriever / pilot: by plant

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| Castor | 18 | 100.0% | 72.2% | 100.0% | 100.0% | 66.7% / 83.3% / 88.9% (n=18) | 0 |
| Guava | 17 | 100.0% | 88.2% | 100.0% | 100.0% | 88.2% / 100.0% / 100.0% (n=17) | 0 |
| Tomato | 14 | 100.0% | 78.6% | 100.0% | 100.0% | 78.6% / 100.0% / 100.0% (n=14) | 0 |

production_retriever / pilot: by question style

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| alias_or_scientific | 8 | 100.0% | 75.0% | 100.0% | 100.0% | 75.0% / 87.5% / 87.5% (n=8) | 0 |
| common_name | 27 | 100.0% | 74.1% | 100.0% | 100.0% | 70.4% / 92.6% / 96.3% (n=27) | 0 |
| descriptor | 14 | 100.0% | 92.9% | 100.0% | 100.0% | 92.9% / 100.0% / 100.0% (n=14) | 0 |

production_retriever / combined: by category

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| identity | 9 | 100.0% | 77.8% | 100.0% | 100.0% | 77.8% / 100.0% / 100.0% (n=9) | 0 |
| misconceptions | 5 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| phytochemistry | 6 | 100.0% | 83.3% | 100.0% | 100.0% | 83.3% / 100.0% / 100.0% (n=6) | 0 |
| preparation | 6 | 100.0% | 83.3% | 100.0% | 100.0% | 75.0% / 100.0% / 100.0% (n=4) | 0 |
| safety_precautions | 33 | 100.0% | 69.7% | 100.0% | 100.0% | 79.0% / 94.7% / 100.0% (n=19) | 0 |
| therapeutic_uses | 30 | 100.0% | 90.0% | 100.0% | 100.0% | 72.7% / 81.8% / 81.8% (n=11) | 0 |

production_retriever / combined: by plant

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| Aloe Vera | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Amla | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Arjuna | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Ashwagandha | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Bael | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Bhringraj | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Brahmi | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Castor | 18 | 100.0% | 72.2% | 100.0% | 100.0% | 66.7% / 83.3% / 88.9% (n=18) | 0 |
| Curry Leaves | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Fenugreek | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Garlic | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Giloy | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Ginger | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Guava | 17 | 100.0% | 88.2% | 100.0% | 100.0% | 88.2% / 100.0% / 100.0% (n=17) | 0 |
| Hibiscus | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Lemongrass | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Mint | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Moringa | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Neem | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Shatavari | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Tomato | 14 | 100.0% | 78.6% | 100.0% | 100.0% | 78.6% / 100.0% / 100.0% (n=14) | 0 |
| Tulsi | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Turmeric | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |

production_retriever / combined: by question style

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| alias_or_scientific | 8 | 100.0% | 75.0% | 100.0% | 100.0% | 75.0% / 87.5% / 87.5% (n=8) | 0 |
| common_name | 27 | 100.0% | 74.1% | 100.0% | 100.0% | 70.4% / 92.6% / 96.3% (n=27) | 0 |
| descriptor | 14 | 100.0% | 92.9% | 100.0% | 100.0% | 92.9% / 100.0% / 100.0% (n=14) | 0 |

production_retriever: no plant+category hit in top 5: 0

production_retriever: no answer-chunk hit in top 5: 2
- [Castor / therapeutic_uses] What is castor oil used for? -> ['Castor#3', 'Castor#9', 'Castor#7', 'Castor#13', 'Castor#16']
- [Castor / therapeutic_uses] What are the pharmacopoeial uses of erand oil? -> ['Castor#10', 'Castor#3', 'Castor#8', 'Castor#15', 'Castor#13']

### raw_faiss

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| original | 40 | 100.0% | 82.5% | 100.0% | 100.0% | - | 0 |
| pilot | 49 | 100.0% | 79.6% | 100.0% | 100.0% | 77.5% / 93.9% / 95.9% (n=49) | 0 |
| combined | 89 | 100.0% | 80.9% | 100.0% | 100.0% | 77.5% / 93.9% / 95.9% (n=49) | 0 |

raw_faiss / original: by category

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| misconceptions | 5 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| preparation | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| safety_precautions | 14 | 100.0% | 57.1% | 100.0% | 100.0% | - | 0 |
| therapeutic_uses | 19 | 100.0% | 94.7% | 100.0% | 100.0% | - | 0 |

raw_faiss / original: by plant

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| Aloe Vera | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Amla | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Arjuna | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Ashwagandha | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Bael | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Bhringraj | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Brahmi | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Curry Leaves | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Fenugreek | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Garlic | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Giloy | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Ginger | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Hibiscus | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Lemongrass | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Mint | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Moringa | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Neem | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Shatavari | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Tulsi | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Turmeric | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |

raw_faiss / pilot: by category

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| identity | 9 | 100.0% | 77.8% | 100.0% | 100.0% | 77.8% / 100.0% / 100.0% (n=9) | 0 |
| phytochemistry | 6 | 100.0% | 83.3% | 100.0% | 100.0% | 83.3% / 100.0% / 100.0% (n=6) | 0 |
| preparation | 4 | 100.0% | 75.0% | 100.0% | 100.0% | 75.0% / 100.0% / 100.0% (n=4) | 0 |
| safety_precautions | 19 | 100.0% | 79.0% | 100.0% | 100.0% | 79.0% / 94.7% / 100.0% (n=19) | 0 |
| therapeutic_uses | 11 | 100.0% | 81.8% | 100.0% | 100.0% | 72.7% / 81.8% / 81.8% (n=11) | 0 |

raw_faiss / pilot: by plant

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| Castor | 18 | 100.0% | 72.2% | 100.0% | 100.0% | 66.7% / 83.3% / 88.9% (n=18) | 0 |
| Guava | 17 | 100.0% | 88.2% | 100.0% | 100.0% | 88.2% / 100.0% / 100.0% (n=17) | 0 |
| Tomato | 14 | 100.0% | 78.6% | 100.0% | 100.0% | 78.6% / 100.0% / 100.0% (n=14) | 0 |

raw_faiss / pilot: by question style

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| alias_or_scientific | 8 | 100.0% | 75.0% | 100.0% | 100.0% | 75.0% / 87.5% / 87.5% (n=8) | 0 |
| common_name | 27 | 100.0% | 74.1% | 100.0% | 100.0% | 70.4% / 92.6% / 96.3% (n=27) | 0 |
| descriptor | 14 | 100.0% | 92.9% | 100.0% | 100.0% | 92.9% / 100.0% / 100.0% (n=14) | 0 |

raw_faiss / combined: by category

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| identity | 9 | 100.0% | 77.8% | 100.0% | 100.0% | 77.8% / 100.0% / 100.0% (n=9) | 0 |
| misconceptions | 5 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| phytochemistry | 6 | 100.0% | 83.3% | 100.0% | 100.0% | 83.3% / 100.0% / 100.0% (n=6) | 0 |
| preparation | 6 | 100.0% | 83.3% | 100.0% | 100.0% | 75.0% / 100.0% / 100.0% (n=4) | 0 |
| safety_precautions | 33 | 100.0% | 69.7% | 100.0% | 100.0% | 79.0% / 94.7% / 100.0% (n=19) | 0 |
| therapeutic_uses | 30 | 100.0% | 90.0% | 100.0% | 100.0% | 72.7% / 81.8% / 81.8% (n=11) | 0 |

raw_faiss / combined: by plant

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| Aloe Vera | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Amla | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Arjuna | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Ashwagandha | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Bael | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Bhringraj | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Brahmi | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Castor | 18 | 100.0% | 72.2% | 100.0% | 100.0% | 66.7% / 83.3% / 88.9% (n=18) | 0 |
| Curry Leaves | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Fenugreek | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Garlic | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Giloy | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Ginger | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Guava | 17 | 100.0% | 88.2% | 100.0% | 100.0% | 88.2% / 100.0% / 100.0% (n=17) | 0 |
| Hibiscus | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Lemongrass | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Mint | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Moringa | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Neem | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Shatavari | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |
| Tomato | 14 | 100.0% | 78.6% | 100.0% | 100.0% | 78.6% / 100.0% / 100.0% (n=14) | 0 |
| Tulsi | 2 | 100.0% | 50.0% | 100.0% | 100.0% | - | 0 |
| Turmeric | 2 | 100.0% | 100.0% | 100.0% | 100.0% | - | 0 |

raw_faiss / combined: by question style

| group | n | plant Hit@1 | plant+cat Hit@1 | Hit@3 | Hit@5 | answer-chunk Hit@1/3/5 | top-1 wrong plant |
|---|---|---|---|---|---|---|---|
| alias_or_scientific | 8 | 100.0% | 75.0% | 100.0% | 100.0% | 75.0% / 87.5% / 87.5% (n=8) | 0 |
| common_name | 27 | 100.0% | 74.1% | 100.0% | 100.0% | 70.4% / 92.6% / 96.3% (n=27) | 0 |
| descriptor | 14 | 100.0% | 92.9% | 100.0% | 100.0% | 92.9% / 100.0% / 100.0% (n=14) | 0 |

raw_faiss: no plant+category hit in top 5: 0

raw_faiss: no answer-chunk hit in top 5: 2
- [Castor / therapeutic_uses] What is castor oil used for? -> ['Castor#3', 'Castor#9', 'Castor#7', 'Castor#13', 'Castor#16']
- [Castor / therapeutic_uses] What are the pharmacopoeial uses of erand oil? -> ['Castor#10', 'Castor#3', 'Castor#8', 'Castor#15', 'Castor#13']
