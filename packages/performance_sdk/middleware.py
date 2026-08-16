"""HTTP latency middleware with privacy-safe operation labels."""
from __future__ import annotations

from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .ports import PerformancePort


class PerformanceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, monitor: PerformancePort) -> None:
        super().__init__(app)
        self._monitor = monitor

    async def dispatch(self, request: Request, call_next) -> Response:
        started = perf_counter()
        success = True
        response: Response | None = None
        try:
            response = await call_next(request)
            success = response.status_code < 500
            return response
        except Exception:
            success = False
            raise
        finally:
            duration_ms = (perf_counter() - started) * 1000
            self._monitor.record(
                "http.request",
                duration_ms,
                success=success,
            )
