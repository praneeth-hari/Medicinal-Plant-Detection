# 🌿 Medicinal Plant Detection & RAG Assistant

A full-stack application that combines **deep learning-based plant detection** with a **Retrieval-Augmented Generation (RAG) chatbot** to identify medicinal plants from images and provide detailed information about their medicinal properties, usage, and precautions.

---

## 🛠️ Tech Stack

| Layer        | Technology                                          |
| ------------ | --------------------------------------------------- |
| **Frontend** | React, Tailwind CSS, Vite                           |
| **Backend**  | FastAPI, Python, SQLAlchemy, Alembic                |
| **ML**       | PyTorch (MobileNetV3-Small), torchvision, Pillow    |
| **RAG**      | FAISS, sentence-transformers, Ollama (`qwen2.5:3b`) |
| **Database** | SQLite                                              |

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+ & npm
- **[Ollama](https://ollama.com)** (for local RAG inference)

---

### Step 1: Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/Medicinal-Plant-RAG.git
cd Medicinal-Plant-RAG
```

#### Windows (PowerShell)
```powershell
# 1. Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install backend & ML dependencies
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install
cd ..
```

#### Linux / macOS / Makefile
```bash
make install
```

---

### Step 2: Environment Variables

Verify or copy the environment configuration files:

```bash
# Backend configuration
cp backend/.env.example backend/.env

# Frontend configuration
cp frontend/.env.example frontend/.env
```

---

### Step 3: Run the Application

#### 1. Start Ollama *(for RAG Chatbot)*
In a terminal, ensure Ollama is running and has the model pulled:
```bash
# Start Ollama service (if not already running in background)
ollama serve

# Pull the required LLM model (one-time setup)
ollama pull qwen2.5:3b
```

#### 2. Start Backend API Server (FastAPI)
Open a terminal in the project root:
- **Windows (PowerShell):**
  ```powershell
  cd backend
  ..\.venv\Scripts\uvicorn main:app --reload --host 127.0.0.1 --port 8000
  ```
- **Linux / macOS:**
  ```bash
  cd backend
  uvicorn main:app --reload --host 127.0.0.1 --port 8000
  ```
- **Or using Make:** `make dev-backend`

> 🔗 **Backend API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)  
> 📖 **Interactive API Docs (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### 3. Start Frontend UI (React + Vite)
Open a **separate** terminal window in the project root:
```bash
cd frontend
npm run dev
```
- **Or using Make:** `make dev-frontend`

> 🌐 **Frontend Web App:** [http://localhost:5173](http://localhost:5173)

---

### 🌐 Ports & Services Summary

| Service | Address | Description |
| :--- | :--- | :--- |
| **Frontend UI** | [http://localhost:5173](http://localhost:5173) | React web application |
| **Backend API** | [http://127.0.0.1:8000](http://127.0.0.1:8000) | FastAPI REST service |
| **API Documentation** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive Swagger UI for testing endpoints |
| **Ollama Service** | `http://localhost:11434` | Local LLM engine (`qwen2.5:3b`) |

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
