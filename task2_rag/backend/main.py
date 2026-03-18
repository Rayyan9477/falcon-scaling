"""FastAPI application entry point with lifespan-based initialization."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import set_engine
from api.v1.router import router as v1_router
from config import settings
from core.embeddings import EmbeddingModel
from core.ingest import build_index, load_dataset, load_index
from core.llm import LLMClient
from core.query_engine import QueryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize embedding model, FAISS index, and query engine on startup."""
    logger.info("Initializing embedding model: %s", settings.embedding_model)
    embedding_model = EmbeddingModel(settings.embedding_model)

    # Try to load existing index, rebuild if not found
    cached = load_index(settings.index_dir)
    if cached:
        logger.info("Loaded existing FAISS index from disk.")
        index, documents, metadata = cached
        df = load_dataset(settings.dataset_path)
    else:
        logger.info("Building FAISS index from dataset: %s", settings.dataset_path)
        index, documents, metadata, df = build_index(
            settings.dataset_path, settings.index_dir, embedding_model
        )
        logger.info("FAISS index built and saved. %d documents indexed.", len(documents))

    # Initialize LLM client
    llm_client = LLMClient(model=settings.llm_model, api_key=settings.llm_api_key)

    # Create query engine and register globally
    engine = QueryEngine(
        faiss_index=index,
        documents=documents,
        metadata=metadata,
        df=df,
        embedding_model=embedding_model,
        llm_client=llm_client,
    )
    set_engine(engine)
    logger.info("Query engine ready. %d records loaded.", len(documents))

    yield  # App runs here

    logger.info("Shutting down.")


app = FastAPI(
    title="PolarityIQ Family Office Intelligence RAG",
    description="Natural language query interface for family office intelligence data",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
app.include_router(v1_router)


@app.get("/")
def root():
    return {"message": "PolarityIQ Family Office Intelligence RAG API", "docs": "/docs"}
