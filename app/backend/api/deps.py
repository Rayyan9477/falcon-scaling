"""Dependency injection for FastAPI endpoints."""

from core.query_engine import QueryEngine
from core.history import QueryHistory

# Global query engine instance (initialized during app lifespan)
_engine: QueryEngine | None = None
_history: QueryHistory | None = None


def set_engine(engine: QueryEngine) -> None:
    global _engine
    _engine = engine


def get_engine() -> QueryEngine:
    if _engine is None:
        raise RuntimeError("Query engine not initialized. Server is still starting up.")
    return _engine


def set_history(history: QueryHistory) -> None:
    global _history
    _history = history


def get_history() -> QueryHistory:
    if _history is None:
        raise RuntimeError("Query history not initialized.")
    return _history
