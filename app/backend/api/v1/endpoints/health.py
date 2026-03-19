"""Health check endpoint."""

from fastapi import APIRouter, Depends

from api.deps import get_engine
from api.v1.schemas.query import HealthResponse
from config import settings
from core.query_engine import QueryEngine

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(engine: QueryEngine = Depends(get_engine)):
    return HealthResponse(
        status="ok",
        records=len(engine.documents),
        index_loaded=engine.index is not None,
        model=settings.llm_model,
    )
