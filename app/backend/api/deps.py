"""Dependency injection for FastAPI endpoints."""

from core.query_engine import QueryEngine

# Global query engine instance (initialized during app lifespan)
_engine: QueryEngine | None = None


def set_engine(engine: QueryEngine) -> None:
    global _engine
    _engine = engine


def get_engine() -> QueryEngine:
    if _engine is None:
        raise RuntimeError("Query engine not initialized. Server is still starting up.")
    return _engine
