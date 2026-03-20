"""Token-bucket rate limiter middleware for FastAPI."""

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimiter:
    """Simple in-memory token-bucket rate limiter keyed by client IP."""

    def __init__(self, requests_per_minute: int = 30, burst: int = 10):
        self.rate = requests_per_minute / 60.0  # tokens per second
        self.burst = burst
        self._buckets: dict[str, dict] = defaultdict(
            lambda: {"tokens": burst, "last": time.monotonic()}
        )

    def allow(self, key: str) -> tuple[bool, dict]:
        """Check if a request is allowed. Returns (allowed, info)."""
        now = time.monotonic()
        bucket = self._buckets[key]

        # Refill tokens
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, {
                "remaining": int(bucket["tokens"]),
                "limit": self.burst,
                "reset": int((self.burst - bucket["tokens"]) / self.rate),
            }
        else:
            retry_after = int((1 - bucket["tokens"]) / self.rate) + 1
            return False, {
                "remaining": 0,
                "limit": self.burst,
                "retry_after": retry_after,
            }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that enforces per-IP rate limiting."""

    def __init__(self, app, requests_per_minute: int = 30, burst: int = 10):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute=requests_per_minute, burst=burst)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks and static files
        if request.url.path in ("/api/v1/health", "/docs", "/openapi.json"):
            return await call_next(request)

        # Only rate-limit API endpoints
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        allowed, info = self.limiter.allow(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please slow down.",
                    "retry_after": info["retry_after"],
                },
                headers={
                    "Retry-After": str(info["retry_after"]),
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        return response
