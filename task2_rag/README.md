# Task 2 — RAG Pipeline: Family Office Intelligence Query System

## Architecture

Full-stack RAG application: **React.js** frontend + **FastAPI** backend + **FAISS** vector search + **LiteLLM** (model-agnostic LLM).

```
React.js (Vite + TS + Tailwind)  →  FastAPI  →  LiteLLM → Any LLM
                                               ├→ FAISS (semantic search)
                                               └→ Pandas (structured filtering)
```

### Dual Retrieval Strategy

Queries are analyzed by the LLM to extract:
1. **Semantic intent** → embedded and searched via FAISS (cosine similarity)
2. **Structured filters** → applied via Pandas DataFrame (numeric/categorical)

Results are merged and the LLM generates a grounded answer with citations.

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, TanStack Query | Modern, type-safe, responsive UI |
| Backend | FastAPI, Pydantic v2, Python 3.11+ | Async API with auto-generated docs |
| LLM | LiteLLM (model-agnostic) | Swap between OpenAI, Anthropic, Groq, Ollama via env var |
| Vector Search | FAISS (faiss-cpu) | Proven at scale, lightweight, pure vector similarity |
| Structured Filter | Pandas DataFrame | Best practice for numeric/analytical queries on tabular data |
| Embeddings | all-MiniLM-L6-v2 (sentence-transformers) | Free, 384-dim, no API cost |

## Setup

### Backend
```bash
cd backend
cp .env.example .env     # Add your LLM API key
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check + index status |
| GET | `/api/v1/filters` | Available filter options for UI |
| GET | `/api/v1/stats` | Dataset statistics |
| POST | `/api/v1/query` | Natural language query |

### Example Query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Which family offices focus on AI with check sizes above $10M?"}'
```

## Chunking Strategy

**Per-Record Rich-Text Documents**: Each of the 200 FO records becomes one document containing all 45 fields in a narrativized format. This preserves entity integrity — a single family office is never split across chunks.

Metadata (region, type, AUM, check size, sector) is stored separately in the Pandas DataFrame for structured filtering.

## Embedding Model

**all-MiniLM-L6-v2** (sentence-transformers): 384 dimensions, 22M parameters. Selected for zero API cost, offline capability, and sufficient quality for 200-document retrieval. With only 200 documents, embedding speed is irrelevant — quality matters more.

## What Failed / Limitations

1. **Last Deal Date** field is generic ("2024-2025 est.") across most records — limits temporal query precision
2. **Phone numbers** are all "lookup required" — not real contact data
3. **LinkedIn URLs** are pattern-generated, not verified
4. Pure semantic search struggles with precise numeric queries — the dual retrieval approach mitigates this
5. LLM-based filter extraction occasionally misclassifies ambiguous queries

## What I Would Improve With More Time

1. **Streaming responses** via SSE for real-time answer generation
2. **Reranking** with a cross-encoder model after initial retrieval
3. **Query history** persistence and conversation memory
4. **Export functionality** for query results (CSV download)
5. **Real-time data enrichment** via news API integration
6. **Authentication** and rate limiting for production deployment
7. **Hybrid embedding** using both dense (FAISS) and sparse (BM25) retrieval
