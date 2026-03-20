# Single-container deployment: FastAPI backend serves React frontend static files.
# Build from repo root: docker build -t falcon-scaling .

# -- Stage 1: Build the React frontend --
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY app/frontend/package.json app/frontend/package-lock.json* app/frontend/.npmrc ./
RUN npm install --legacy-peer-deps --no-audit
COPY app/frontend/ .
RUN npm run build

# -- Stage 2: Python backend + built frontend --
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app/backend/ .

# Copy dataset
COPY data/ /app/data/

# Copy built frontend static files
COPY --from=frontend-build /build/dist ./static/

# Environment defaults (override via Render/Railway dashboard env vars)
ENV DATASET_PATH=/app/data/family_office_dataset.xlsx
ENV INDEX_DIR=/app/index
ENV EMBEDDING_MODEL=text-embedding-3-small
ENV LLM_MODEL=gpt-4o
ENV CORS_ORIGINS=*

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
