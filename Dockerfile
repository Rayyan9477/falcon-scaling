# Single-container deployment: FastAPI backend serves React frontend static files.
# This keeps deployment simple — one service, one URL, one process.

# ── Stage 1: Build the React frontend ───────────────────────────────
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY app/frontend/package.json app/frontend/package-lock.json ./
RUN npm ci --no-audit
COPY app/frontend/ .
RUN npm run build

# ── Stage 2: Python backend + built frontend ────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app/backend/ .

# Copy pre-computed FAISS index (avoids rebuilding on cold start)
COPY app/backend/index/ ./index/

# Copy dataset
COPY data/ ./data/

# Copy built frontend static files
COPY --from=frontend-build /build/dist ./static/

# Environment defaults (override via Render/Railway dashboard)
ENV DATASET_PATH=/app/data/family_office_dataset.xlsx
ENV EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV LLM_MODEL=gpt-5.4-nano
ENV CORS_ORIGINS=*

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
