# Development Environment Setup

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- [Ollama](https://ollama.com), with the model pulled: `ollama pull qwen2.5:3b`

## Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (source .venv/bin/activate on Linux/macOS)

cd backend
pip install -r requirements.txt
pip install -r ../ml/requirements.txt

cp .env.example .env            # then edit if needed
alembic upgrade head            # optional: tables are also created on startup

# One-time: seed plants and build the search index
python scripts/seed_plants.py
python scripts/build_index.py

uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:3000 (proxies /api to :8000)
```

## Tests

Run from the repository root: `pytest tests -v`. Tests use a temporary database and
never touch your real data.

## Environment variables (`backend/.env`)

| Variable              | Description                          | Default                       |
| --------------------- | ------------------------------------ | ----------------------------- |
| `DATABASE_URL`        | Database connection string           | `sqlite+aiosqlite:///./medicinal_plants.db` |
| `OLLAMA_BASE_URL`     | Ollama server                        | `http://localhost:11434`      |
| `OLLAMA_MODEL`        | Model used for chat answers          | `qwen2.5:3b`                  |
| `EMBEDDING_MODEL`     | Sentence-transformer model           | `all-MiniLM-L6-v2`            |
| `UPLOAD_DIR`          | Where uploaded images are stored     | `./data/uploads`              |
| `SERVICENOW_*`        | Optional CMDB sync credentials       | empty                         |

## Troubleshooting

- **Chat says "ollama pull ..."**: Ollama is not running or the model is not installed.
- **Plants show "No Monograph Available"**: the plant is not in the database; only 20 plants
  are seeded.
- **Empty chat sources**: run `python scripts/build_index.py` from `backend/`.
