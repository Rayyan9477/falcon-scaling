"""Query endpoint — POST /api/v1/query."""

from fastapi import APIRouter, Depends

from api.deps import get_engine
from api.v1.schemas.query import QueryRequest, QueryResponse, FamilyOfficeResult, QueryAnalysis
from core.query_engine import QueryEngine

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_dataset(request: QueryRequest, engine: QueryEngine = Depends(get_engine)):
    """Query the family office dataset using natural language."""

    # Convert UI filters to dict if provided
    ui_filters = None
    if request.filters:
        ui_filters = request.filters.model_dump(exclude_none=True)
        # Remove empty lists
        ui_filters = {k: v for k, v in ui_filters.items() if v != []}

    result = await engine.query(
        user_query=request.query,
        ui_filters=ui_filters,
        top_k=request.top_k,
    )

    return QueryResponse(
        answer=result["answer"],
        sources=[FamilyOfficeResult(**s) for s in result["sources"]],
        query_analysis=QueryAnalysis(**result["query_analysis"]),
        total_matches=result["total_matches"],
    )
