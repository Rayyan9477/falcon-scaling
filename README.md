# Falcon Scaling / PolarityIQ — 72-Hour Differentiator

## Overview

Four-task evaluation for Falcon Scaling / PolarityIQ covering dataset creation, RAG pipeline engineering, SaaS conversion analysis, and AI product development.

## Project Structure

| Directory | Task | Description |
|-----------|------|-------------|
| `data/` | Shared | Final validated Family Office Intelligence dataset (200 records, 45 fields) |
| `task1_dataset/` | Task 1 | Dataset creation methodology documentation |
| `task2_rag/` | Task 2 | Full-stack RAG pipeline (FastAPI + React + FAISS + LiteLLM) |
| `task3_conversion/` | Task 3 | PolarityIQ SaaS conversion analysis |
| `task4_product/` | Task 4 | Co-Investment Intelligence Accelerator (trip-wire product) |

## Task 1 — Dataset Creation (Complete)

- **200 validated records** of international family offices
- **45 intelligence fields** per record (identity, contacts, investment profile, signals, relationships, governance)
- Covers 6 regions, 30+ countries, SFO/MFO classification
- AUM range: $0.2B to $224.5B

## Task 2 — RAG Pipeline

Full-stack application making the dataset queryable via natural language.

**Architecture**: React.js (Vite + TypeScript + Tailwind) → FastAPI → LiteLLM (model-agnostic) + FAISS (vector search) + Pandas (structured filtering)

See [task2_rag/README.md](task2_rag/README.md) for setup and documentation.

## Task 3 — SaaS Conversion Analysis

Evidence-based plan to improve PolarityIQ free trial → paid conversion rate.

See [task3_conversion/](task3_conversion/)

## Task 4 — AI Product Build

"Co-Investment Intelligence Accelerator" — a $197 trip-wire product for investors.

See [task4_product/](task4_product/)

## Quick Start (Task 2)

```bash
# Backend
cd task2_rag/backend
cp .env.example .env  # Add your API key
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd task2_rag/frontend
npm install
npm run dev
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, FAISS, LiteLLM, sentence-transformers, Pandas
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, TanStack Query
- **LLM**: Any provider via LiteLLM (OpenAI, Anthropic, Groq, Ollama, etc.)
- **Deployment**: Docker Compose → Render / Railway / Vercel
