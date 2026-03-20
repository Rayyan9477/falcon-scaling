"""API v1 router — aggregates all v1 endpoints."""

from fastapi import APIRouter

from api.v1.endpoints import health, query, filters, history

router = APIRouter(prefix="/api/v1")
router.include_router(health.router, tags=["health"])
router.include_router(query.router, tags=["query"])
router.include_router(filters.router, tags=["filters"])
router.include_router(history.router, tags=["history"])
