"""FastAPI application entry point with lifespan-based initialization."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
        df = load_dataset(settings.dataset_path).reset_index(drop=True)
    else:
        logger.info("Building FAISS index from dataset: %s", settings.dataset_path)
        index, documents, metadata, df = build_index(
            settings.dataset_path, settings.index_dir, embedding_model
        )
        df = df.reset_index(drop=True)
        logger.info("FAISS index built and saved. %d documents indexed.", len(documents))

    # Initialize LLM client (with automatic fallback to GPT-4o-mini if primary fails)
    llm_client = LLMClient(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        api_base=settings.llm_api_base or None,
        fallback_api_key=settings.llm_fallback_api_key or None,
    )

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

# Serve React frontend static files in production (when built with `npm run build`)
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    logger.info("Serving frontend static files from %s", STATIC_DIR)
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve React SPA — all non-API routes fall through to index.html."""
        file_path = STATIC_DIR / path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "PolarityIQ Family Office Intelligence API", "docs": "/docs"}
