# 🏗️ Architecture Overview

> **Status:** Stub — this document will be populated with detailed architecture diagrams and descriptions.

## High-Level Architecture

<!-- TODO: Add architecture diagram (Mermaid or image) -->

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Frontend   │────▶│   Backend    │────▶│   Database       │
│  (React/TS)  │◀────│  (FastAPI)   │◀────│  (PostgreSQL)    │
└─────────────┘     └──────┬───────┘     └──────────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────▼─────┐ ┌─────▼─────┐
              │  ML Model  │ │    RAG    │
              │ (PyTorch)  │ │ Pipeline  │
              └───────────┘ └─────┬─────┘
                                  │
                           ┌──────▼──────┐
                           │  ChromaDB   │
                           │ (Vectors)   │
                           └─────────────┘
```

## Component Descriptions

### Frontend
- **Technology:** React, TypeScript, Tailwind CSS, Vite
- **Responsibility:** User interface for image upload, plant browsing, and chat

### Backend
- **Technology:** FastAPI, SQLAlchemy, Alembic
- **Responsibility:** REST API, authentication, business logic orchestration

### ML Model
- **Technology:** PyTorch, torchvision
- **Responsibility:** Image classification for plant species identification

### RAG Pipeline
- **Technology:** LangChain, OpenAI, ChromaDB
- **Responsibility:** Retrieval-augmented generation for plant knowledge Q&A

### Database
- **Technology:** PostgreSQL (production), SQLite (development)
- **Responsibility:** Persistent storage for users, plants, detections, chat history

## Data Flow

<!-- TODO: Add detailed data flow diagrams -->

1. **Image Detection Flow:** User uploads image → Backend → ML Model → Prediction → Database → Response
2. **Chat/RAG Flow:** User sends query → Backend → RAG Pipeline → ChromaDB retrieval → LLM generation → Response

## Security Considerations

<!-- TODO: Document authentication, authorization, and data protection strategies -->
