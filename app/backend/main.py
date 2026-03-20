"""FastAPI application entry point with lifespan-based initialization."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.deps import set_engine, set_history
from api.v1.router import router as v1_router
from config import settings
from core.embeddings import EmbeddingModel
from core.ingest import build_index, load_dataset, load_index
from core.llm import LLMClient
from core.query_engine import QueryEngine
from core.history import QueryHistory
from core.rate_limiter import RateLimitMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize embedding model, vector index, and query engine on startup."""
    api_key = settings.llm_api_key
    if not api_key or api_key.startswith("sk-your"):
        logger.error("=" * 60)
        logger.error("  NO VALID API KEY FOUND!")
        logger.error("  Edit app/backend/.env and set LLM_API_KEY=sk-...")
        logger.error("  The server will start but queries will fail.")
        logger.error("=" * 60)

    logger.info("Initializing embedding model: %s", settings.embedding_model)
    embedding_model = EmbeddingModel(settings.embedding_model, api_key=api_key)

    # Try to load existing index, rebuild if not found
    cached = load_index(settings.index_dir)
    if cached:
        logger.info("Loaded existing vector index from disk.")
        embeddings, documents, metadata = cached
        df = load_dataset(settings.dataset_path).reset_index(drop=True)
    else:
        if not api_key or api_key.startswith("sk-your"):
            logger.error("Cannot build vector index without a valid OpenAI API key.")
            logger.error("Set LLM_API_KEY in app/backend/.env, then restart.")
            # Load dataset but use empty embeddings so server can still start
            df = load_dataset(settings.dataset_path).reset_index(drop=True)
            import numpy as np
            documents = []
            metadata = []
            from core.ingest import row_to_document, row_to_metadata
            for _, row in df.iterrows():
                documents.append(row_to_document(row))
                metadata.append(row_to_metadata(row))
            embeddings = np.zeros((len(documents), 1536), dtype=np.float32)
            logger.warning("Using zero embeddings -- semantic search will NOT work until index is built.")
        else:
            logger.info("Building vector index from dataset: %s", settings.dataset_path)
            embeddings, documents, metadata, df = build_index(
                settings.dataset_path, settings.index_dir, embedding_model
            )
            df = df.reset_index(drop=True)
            logger.info("Vector index built and saved. %d documents indexed.", len(documents))

    # Initialize LLM client
    llm_client = LLMClient(
        model=settings.llm_model,
        api_key=api_key,
        api_base=settings.llm_api_base or None,
        fallback_api_key=settings.llm_fallback_api_key or None,
    )

    # Create query engine and register globally
    engine = QueryEngine(
        embeddings=embeddings,
        documents=documents,
        metadata=metadata,
        df=df,
        embedding_model=embedding_model,
        llm_client=llm_client,
    )
    set_engine(engine)

    # Initialize query history with file persistence
    history_path = str(Path(__file__).resolve().parent / "index" / "query_history.json")
    history = QueryHistory(persist_path=history_path)
    set_history(history)
    logger.info("Query engine ready. %d records loaded.", len(documents))

    yield  # App runs here

    logger.info("Shutting down.")


app = FastAPI(
    title="PolarityIQ Family Office Intelligence RAG",
    description="Natural language query interface for family office intelligence data",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting (30 requests/min per IP, burst of 10)
app.add_middleware(RateLimitMiddleware, requests_per_minute=30, burst=10)

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
        """Serve React SPA -- all non-API routes fall through to index.html."""
        file_path = STATIC_DIR / path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "PolarityIQ Family Office Intelligence API", "docs": "/docs"}
