# Architecture Overview

```
┌────────────┐   /api/v1   ┌───────────────────────────────────────────┐
│  Frontend  │────────────▶│ FastAPI backend                           │
│ React/Vite │◀────────────│ endpoints → services → repositories → DB  │
└────────────┘             └───┬───────────────┬───────────────────────┘
                               │               │
                      ┌────────▼───────┐ ┌─────▼────────────────────────┐
                      │ ml/predict.py  │ │ RAG pipeline (backend/rag)   │
                      │ MobileNetV3    │ │ MiniLM embeddings → FAISS    │
                      │ (PyTorch)      │ │ → Ollama (qwen2.5:3b)        │
                      └────────────────┘ └──────────────────────────────┘
```

## Components

- **Frontend** (`frontend/`): React 18, Vite, Tailwind. Pages for plant catalog, detection
  (upload or webcam), RAG chat, plant comparison, PubMed research search, history,
  favorites (browser storage), settings and the AI Control Tower.
- **Backend** (`backend/`): FastAPI with async SQLAlchemy on SQLite. Layers:
  `api/v1/endpoints` (HTTP) → `services` (business rules) → `repositories` (queries) →
  `models` (ORM). Alembic migrations live in `backend/migrations`.
- **Classifier** (`ml/`): MobileNetV3-Small fine-tuned on 78 plant classes. Weights and the
  class list are in `backend/data/models/`. `train.py` trains and writes
  `backend/data/training_metrics_report.json`.
- **RAG** (`backend/rag/`): `all-MiniLM-L6-v2` embeddings, a FAISS inner-product index
  (`backend/data/embeddings/`), a retriever that boosts chunks for plants named in the
  query and limits repeats per plant, and a generator that calls the local Ollama server.
  The knowledge base text is in `backend/scripts/build_index.py` (rebuild the index with
  `python scripts/build_index.py` from `backend/`).
- **Evidence model** (`backend/schemas/evidence_schema.py`, `plant_validator.py`): a
  structured plant record (claims with evidence levels, drug interactions, safety warnings,
  dosage) and 15 validation rules used when seeding reviewed plants.
- **Governance** (Control Tower): guardrails applied in `ChatService` — toxicity filter,
  PII masking, dosage disclaimer, source verification — with an audit log and live telemetry.

## Data flow

1. **Detection:** upload → saved to `UPLOAD_DIR` → `ml.predict.predict` → names mapped to
   database plants → `DetectionResult` stored → response.
2. **Chat:** question → guardrails → retrieve top chunks from FAISS → Ollama generates a
   grounded answer with `[Source N]` citations → stored with sources → audit + metrics.

## Security

The app has no login: every request acts as one local user, so it is intended to run on a
trusted machine (localhost). Do not expose it to the internet as is.
