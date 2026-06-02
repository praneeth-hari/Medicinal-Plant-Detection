# 🌿 Medicinal Plant Detection & RAG Assistant

A full-stack application that combines **deep learning-based plant detection** with a **Retrieval-Augmented Generation (RAG) chatbot** to identify medicinal plants from images and provide detailed information about their medicinal properties, usage, and precautions.

---

## 🛠️ Tech Stack

| Layer        | Technology                              |
| ------------ | --------------------------------------- |
| **Frontend** | React, TypeScript, Tailwind CSS, Vite   |
| **Backend**  | FastAPI, Python, SQLAlchemy, Alembic    |
| **ML**       | PyTorch, torchvision, Pillow            |
| **RAG**      | LangChain, ChromaDB, OpenAI Embeddings |
| **Database** | PostgreSQL / SQLite (dev)               |
| **DevOps**   | Docker, Docker Compose, Nginx           |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Medicinal-Plant-RAG.git
cd Medicinal-Plant-RAG

# Install all dependencies
make install

# Set up environment variables
cp deployment/.env.production.example .env
# Edit .env with your configuration
```

### Development

```bash
# Run backend dev server
make dev-backend

# Run frontend dev server
make dev-frontend

# Run both concurrently
make dev
```

### Docker

```bash
# Start all services
make docker-up

# Stop all services
make docker-down
```

---

## 📁 Project Structure

```
Medicinal-Plant-RAG/
├── backend/               # FastAPI backend application
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   ├── core/          # App configuration & security
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic layer
│   │   └── rag/           # RAG pipeline components
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page-level components
│   │   ├── services/      # API client services
│   │   └── hooks/         # Custom React hooks
│   └── package.json
├── ml/                    # Machine learning pipeline
│   ├── train.py           # Model training script
│   ├── evaluate.py        # Model evaluation script
│   ├── predict.py         # Inference script
│   ├── preprocessing.py   # Image preprocessing pipeline
│   ├── model.py           # Model architecture definition
│   └── config.py          # Hyperparameter configuration
├── data/                  # Data storage directories
│   ├── raw/               # Raw dataset files
│   ├── processed/         # Preprocessed datasets
│   ├── models/            # Trained model checkpoints
│   ├── embeddings/        # Vector embeddings
│   ├── uploads/           # User-uploaded images
│   └── knowledge_base/    # RAG knowledge base documents
├── tests/                 # Test suites
├── docs/                  # Project documentation
├── deployment/            # Deployment configurations
├── docker-compose.yml     # Docker Compose orchestration
├── Makefile               # Development convenience targets
└── README.md              # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

<!-- TODO: Add CONTRIBUTING.md with detailed guidelines -->

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<!-- TODO: Add LICENSE file -->
