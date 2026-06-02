# 📂 Data Directory Structure

This directory contains all data assets for the Medicinal Plant Detection & RAG Assistant.

## Subdirectories

| Directory        | Purpose                                                                 |
| ---------------- | ----------------------------------------------------------------------- |
| `raw/`           | Raw, unprocessed dataset files (images, labels, metadata)               |
| `processed/`     | Preprocessed and augmented datasets ready for model training            |
| `models/`        | Trained model checkpoints (`.pt`, `.pth` files)                         |
| `embeddings/`    | Vector embeddings for the RAG knowledge base (ChromaDB persistence)     |
| `uploads/`       | User-uploaded images for plant identification (temporary storage)       |
| `knowledge_base/`| Source documents for the RAG pipeline (PDFs, markdown, text files)       |

## Notes

- `raw/` is git-ignored — download or link datasets locally.
- `uploads/` contents are ephemeral and git-ignored.
- `models/` checkpoint files (`.pt`, `.pth`) are git-ignored due to size.
- `knowledge_base/` documents are ingested and embedded by the RAG pipeline.
