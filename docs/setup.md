# 🛠️ Development Environment Setup

> **Status:** Stub — detailed instructions will be added as the project matures.

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git
- Docker & Docker Compose (optional, for containerized development)

## Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp ../deployment/.env.production.example .env
# Edit .env with your local configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Start the development server
npm run dev
```

## ML Environment Setup

```bash
# Install ML dependencies (in the same or separate virtualenv)
cd ml
pip install -r requirements.txt
```

## Environment Variables

<!-- TODO: Document all required environment variables -->

| Variable          | Description                     | Default       |
| ----------------- | ------------------------------- | ------------- |
| `DATABASE_URL`    | Database connection string      | `sqlite:///…` |
| `SECRET_KEY`      | JWT signing secret              | —             |
| `OPENAI_API_KEY`  | OpenAI API key for embeddings   | —             |
| `ENVIRONMENT`     | Runtime environment             | `development` |

## Troubleshooting

<!-- TODO: Add common setup issues and solutions -->
