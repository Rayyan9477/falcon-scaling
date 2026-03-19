"""Filter and stats endpoints."""

from fastapi import APIRouter, Depends

from api.deps import get_engine
from api.v1.schemas.query import FilterOptions, StatsResponse
from core.query_engine import QueryEngine

router = APIRouter()


@router.get("/filters", response_model=FilterOptions)
def get_filters(engine: QueryEngine = Depends(get_engine)):
    """Return available filter values for UI dropdowns."""
    return FilterOptions(**engine.get_filter_options())


@router.get("/stats", response_model=StatsResponse)
def get_stats(engine: QueryEngine = Depends(get_engine)):
    """Return dataset statistics."""
    return StatsResponse(**engine.get_stats())
