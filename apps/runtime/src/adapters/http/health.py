"""
Astera Kernel — HTTP Health & Version Adapter.

Exposes Kernel state over HTTP. All routes call KernelPort (inbound port) —
never the AsteraKernel class directly.

Endpoints:
    GET /health    → Liveness   — always 200 if the process is alive
    GET /live      → Liveness   — alias (Kubernetes convention)
    GET /ready     → Readiness  — 200 only when Kernel state is READY/DEGRADED
    GET /status    → Full Kernel status summary
    GET /version   → Build and version information
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from apps.runtime.src.ports.inbound import KernelPort

router = APIRouter(tags=["Kernel"])


def create_health_router(kernel: KernelPort) -> APIRouter:
    """
    Factory that creates all health/version routes with the Kernel injected.

    Args:
        kernel: The KernelPort implementation (AsteraKernel).

    Returns:
        A configured APIRouter.
    """

    @router.get(
        "/health",
        summary="Liveness probe",
        description=(
            "Returns 200 as long as the process is alive. "
            "Used by Docker HEALTHCHECK and Kubernetes liveness probes."
        ),
    )
    async def liveness() -> JSONResponse:
        return JSONResponse(content={"status": "alive"})

    @router.get(
        "/live",
        summary="Liveness probe (Kubernetes alias)",
        description="Kubernetes-style liveness probe. Identical to /health.",
    )
    async def live() -> JSONResponse:
        return JSONResponse(content={"status": "alive"})

    @router.get(
        "/ready",
        summary="Readiness probe",
        description=(
            "Returns 200 when the Kernel is READY or DEGRADED. "
            "Returns 503 while BOOTING or after FAILED. "
            "Used by Kubernetes readiness probes."
        ),
    )
    async def readiness() -> JSONResponse:
        if not kernel.is_ready():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "not_ready", "reason": "Kernel is not yet operational."},
            )
        try:
            health = await kernel.get_health()
            return JSONResponse(content={"status": "ready", **health})
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "not_ready", "reason": str(exc)},
            )

    @router.get(
        "/status",
        summary="Kernel status",
        description="Full Kernel status: state, uptime, components, capabilities, context.",
    )
    async def kernel_status() -> JSONResponse:
        try:
            result = await kernel.get_status()
            return JSONResponse(content=result)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            )

    @router.get(
        "/version",
        summary="Platform version",
        description=(
            "Returns build and version information for the Astera platform. "
            "Useful for CI/CD validation, Grafana annotations, and debugging."
        ),
    )
    async def version() -> JSONResponse:
        return JSONResponse(content=kernel.get_version_info())

    return router
