"""Query history endpoints."""

from fastapi import APIRouter, Depends, Query

from api.deps import get_history
from api.v1.schemas.query import HistoryEntry
from core.history import QueryHistory

router = APIRouter()


@router.get("/history", response_model=list[HistoryEntry])
def list_history(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    history: QueryHistory = Depends(get_history),
):
    """Return query history, newest first."""
    entries = history.get_all(limit=limit, offset=offset)
    return [HistoryEntry(**e) for e in entries]


@router.delete("/history")
def clear_history(history: QueryHistory = Depends(get_history)):
    """Clear all query history."""
    count = history.clear()
    return {"deleted": count}
