# NOTE: For Render deployment, use the ROOT Dockerfile (../../../Dockerfile)
# with Root Directory set to empty (repo root). This Dockerfile is for
# docker-compose local dev only.
#
# If you must use this one on Render, set Root Directory to "app/backend"
# and mount/upload the dataset separately.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code into /app
COPY . .

# Create data and index dirs
RUN mkdir -p /app/data /app/index

# Environment defaults (override via Render dashboard)
ENV DATASET_PATH=/app/data/family_office_dataset.xlsx
ENV INDEX_DIR=/app/index
ENV EMBEDDING_MODEL=text-embedding-3-small
ENV LLM_MODEL=gpt-4o
ENV CORS_ORIGINS=*

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
