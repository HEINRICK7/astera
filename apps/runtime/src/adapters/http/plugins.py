"""Public plugin discovery and health API adapter."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from apps.runtime.src.ports.inbound import PluginRegistryPort


def create_plugin_router(registry: PluginRegistryPort) -> APIRouter:
    """Create plugin discovery routes for one Kernel instance."""

    router = APIRouter(prefix="/api/v1", tags=["Plugins"])

    @router.get("/plugins")
    async def list_plugins() -> JSONResponse:
        plugins = await registry.list_plugins()
        return JSONResponse(content={
            "success": True,
            "data": plugins,
            "meta": {"count": len(plugins)},
            "trace_id": None,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        })

    @router.get("/plugins/{plugin_name}")
    async def get_plugin(plugin_name: str) -> JSONResponse:
        try:
            plugin = await registry.get_plugin(plugin_name)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"success": False, "error": {"message": str(exc)}},
            ) from exc
        return JSONResponse(content={
            "success": True,
            "data": plugin,
            "meta": {},
            "trace_id": None,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        })

    return router
