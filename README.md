# 🌿 Medicinal Plant Detection & RAG Assistant

A full-stack application that combines **deep learning-based plant detection** with a **Retrieval-Augmented Generation (RAG) chatbot** to identify medicinal plants from images and provide detailed information about their medicinal properties, usage, and precautions.

---

## 🛠️ Tech Stack

| Layer        | Technology                                          |
| ------------ | --------------------------------------------------- |
| **Frontend** | React, Tailwind CSS, Vite                           |
| **Backend**  | FastAPI, Python, SQLAlchemy, Alembic                |
| **ML**       | PyTorch (MobileNetV3-Small), torchvision, Pillow    |
| **RAG**      | FAISS, sentence-transformers, Ollama (qwen2.5:3b)   |
| **Database** | SQLite                                              |

------------ | --------------------------------------- |
| **Frontend** | React, TypeScript, Tailwind CSS, Vite   |
| **Backend**  | FastAPI, Python, SQLAlchemy, Alembic    |
| **ML**       | PyTorch, torchvision, Pillow            |
| **RAG**      | LangChain, ChromaDB, OpenAI Embeddings |
| **Database** | PostgreSQL / SQLite (dev)               |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) with the model pulled: `ollama pull qwen2.5:3b`

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Medicinal-Plant-RAG.git
cd Medicinal-Plant-RAG

# Install all dependencies
make install

# Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
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

---

## 📁 Project Structure

```
Medicinal-Plant-RAG/
├── backend/               # FastAPI backend (run from this folder)
│   ├── main.py            # App entry point
│   ├── api/               # Routes (v1/endpoints) and dependencies
│   ├── services/          # Business logic (chat, detection, plants, ServiceNow)
│   ├── repositories/      # Database access layer
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic schemas (incl. evidence-based plant model + validator)
│   ├── rag/               # Embeddings, FAISS vector store, retriever, Ollama generator
│   ├── scripts/           # Seeding and index-building scripts
│   ├── migrations/        # Alembic migrations
│   └── data/              # Model weights, FAISS index, uploads (git-ignored)
├── frontend/              # React + Vite frontend
│   └── src/               # pages, components, api, context, hooks, utils
├── ml/                    # train.py, predict.py, prepare_dataset.py, model.py
├── data/                  # Image dataset splits (raw/train/val/test, git-ignored)
├── tests/                 # pytest suites
├── docs/                  # Project documentation
└── Makefile               # Dev convenience targets
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
