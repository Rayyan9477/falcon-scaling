"""Query endpoints — POST /api/v1/query and /api/v1/query/stream."""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from api.deps import get_engine, get_history
from api.v1.schemas.query import QueryRequest, QueryResponse, FamilyOfficeResult, QueryAnalysis
from core.query_engine import QueryEngine
from core.history import QueryHistory

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_dataset(
    request: QueryRequest,
    engine: QueryEngine = Depends(get_engine),
    history: QueryHistory = Depends(get_history),
):
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

    response = QueryResponse(
        answer=result["answer"],
        sources=[FamilyOfficeResult(**s) for s in result["sources"]],
        query_analysis=QueryAnalysis(**result["query_analysis"]),
        total_matches=result["total_matches"],
    )

    # Save to history
    history.add(
        query=request.query,
        answer=result["answer"],
        sources=result["sources"],
        query_analysis=result["query_analysis"],
        total_matches=result["total_matches"],
    )

    return response


@router.post("/query/stream")
async def query_dataset_stream(
    request: QueryRequest,
    engine: QueryEngine = Depends(get_engine),
    history: QueryHistory = Depends(get_history),
):
    """Stream query results via Server-Sent Events (SSE)."""

    ui_filters = None
    if request.filters:
        ui_filters = request.filters.model_dump(exclude_none=True)
        ui_filters = {k: v for k, v in ui_filters.items() if v != []}

    async def event_generator():
        full_answer = []
        sources_data = []
        analysis_data = None

        async for event in engine.query_stream(
            user_query=request.query,
            ui_filters=ui_filters,
            top_k=request.top_k,
        ):
            event_type = event["event"]
            data = event["data"]

            if event_type == "sources":
                parsed = json.loads(data)
                sources_data = parsed.get("sources", [])

            if event_type == "token":
                full_answer.append(data)

            if event_type == "done":
                parsed = json.loads(data)
                analysis_data = parsed.get("query_analysis")

            yield f"event: {event_type}\ndata: {data}\n\n"

        # Save completed query to history
        history.add(
            query=request.query,
            answer="".join(full_answer),
            sources=sources_data,
            query_analysis=analysis_data,
            total_matches=len(sources_data),
        )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
