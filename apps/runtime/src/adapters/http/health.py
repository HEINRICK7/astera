"""
Astera Runtime — HTTP Health Adapter (FastAPI Routes).

Exposes the Runtime health state over HTTP.
This adapter calls the RuntimePort (inbound port) — never the application directly.

Routes:
    GET /health        — Liveness probe (is the process alive?)
    GET /health/ready  — Readiness probe (is the Runtime ready for traffic?)
    GET /status        — Full Runtime status summary
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from apps.runtime.src.ports.inbound import RuntimePort

router = APIRouter(tags=["Health"])


def create_health_router(runtime: RuntimePort) -> APIRouter:
    """
    Factory that creates the health router with the Runtime injected.

    Args:
        runtime: The RuntimePort implementation (RuntimeManager).

    Returns:
        A configured APIRouter with health endpoints.
    """

    @router.get(
        "/health",
        summary="Liveness probe",
        description="Returns 200 if the process is alive. Used by Docker/Kubernetes liveness probes.",
    )
    async def liveness() -> JSONResponse:
        """Always returns 200 while the process is running."""
        return JSONResponse(content={"status": "alive"})

    @router.get(
        "/health/ready",
        summary="Readiness probe",
        description="Returns 200 if the Runtime is ready to accept requests.",
    )
    async def readiness() -> JSONResponse:
        """Returns 200 when the Platform Bootstrap is complete."""
        try:
            health = await runtime.get_health()
            return JSONResponse(content={"status": "ready", "health": health})
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "not_ready", "reason": str(exc)},
            )

    @router.get(
        "/status",
        summary="Runtime status",
        description="Returns the full status summary of the Astera Runtime.",
    )
    async def runtime_status() -> JSONResponse:
        """Returns detailed Runtime status including plugins and uptime."""
        try:
            result = await runtime.get_status()
            return JSONResponse(content=result)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            )

    return router
