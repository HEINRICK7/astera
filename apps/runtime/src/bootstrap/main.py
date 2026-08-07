"""
Astera Runtime — Platform Bootstrap.

This is the entry point of the Astera platform.
It executes the Platform Bootstrap sequence in the correct order:

    1. Configure Logging
    2. Load Configuration (AsteraSettings)
    3. Build Dependency Container
    4. Connect Event Bus (NATS)
    5. Initialize Plugin Registry
    6. Initialize Health Manager
    7. Initialize Lifecycle Manager
    8. Start API (FastAPI/Uvicorn)

When this module exits successfully, you have an "Astera vazio" —
a fully operational platform with no clinical logic, ready to accept plugins.

Usage:
    python -m apps.runtime.src.bootstrap.main
    # or via uvicorn:
    uvicorn apps.runtime.src.bootstrap.main:create_app --factory --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Infrastructure ────────────────────────────────────────────────────────────
from apps.runtime.src.infrastructure.settings import get_settings
from apps.runtime.src.infrastructure.logging import configure_logging

# ── Adapters ──────────────────────────────────────────────────────────────────
from apps.runtime.src.adapters.nats import NatsEventBusAdapter
from apps.runtime.src.adapters.http.health import create_health_router

# ── Application ───────────────────────────────────────────────────────────────
from apps.runtime.src.application.runtime import RuntimeManager

logger = logging.getLogger("astera.runtime.bootstrap")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.

    Handles the full Platform Bootstrap sequence on startup
    and graceful shutdown on SIGTERM/SIGINT.

    This replaces the deprecated @app.on_event("startup") pattern.
    """
    runtime: RuntimeManager = app.state.runtime

    # ── STARTUP ───────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("  ASTERA RUNTIME — PLATFORM BOOTSTRAP STARTING")
    logger.info("=" * 60)

    try:
        await runtime.startup()
        logger.info("=" * 60)
        logger.info("  ASTERA RUNTIME — PLATFORM READY")
        logger.info("=" * 60)
    except Exception as exc:
        logger.critical(
            "Platform Bootstrap FAILED — Runtime cannot start",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise SystemExit(1) from exc

    yield  # ← Application is running here

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("  ASTERA RUNTIME — GRACEFUL SHUTDOWN INITIATED")
    logger.info("=" * 60)

    await runtime.shutdown()

    logger.info("=" * 60)
    logger.info("  ASTERA RUNTIME — STOPPED CLEANLY")
    logger.info("=" * 60)


# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    FastAPI application factory.

    Builds the complete Astera Runtime application:
    1. Loads settings
    2. Configures logging
    3. Builds the dependency container
    4. Creates the RuntimeManager
    5. Mounts all adapters (HTTP routes)
    6. Returns the configured FastAPI app

    This factory pattern enables:
    - Testing with different settings
    - Multiple instances in the same process (if needed)
    - Deferred initialization (uvicorn --factory flag)
    """
    # Step 1 — Load configuration
    settings = get_settings()

    # Step 2 — Configure logging (must happen before any log statement)
    configure_logging(
        level=settings.log_level,
        json_format=settings.is_production,
    )

    logger.info(
        "Astera Runtime initializing",
        extra={
            "environment": settings.environment,
            "debug": settings.debug,
            "nats_url": settings.nats_url,
            "otel_endpoint": settings.otel_endpoint,
        },
    )

    # Step 3 — Build Dependency Container
    # Wire up concrete implementations to abstract interfaces.
    # Only place in the codebase where concrete adapters are instantiated.
    event_bus = NatsEventBusAdapter(
        nats_url=settings.nats_url,
        connect_timeout=settings.nats_connect_timeout,
    )

    # Step 4 — Create Runtime Manager (application layer)
    runtime = RuntimeManager(event_bus=event_bus)

    # Step 5 — Create FastAPI application
    app = FastAPI(
        title="Astera Runtime",
        description=(
            "The Astera Runtime is the heart of the Astera platform. "
            "It manages the lifecycle of all platform components, plugins, "
            "and the Event Bus. "
            "\n\n**Architecture:** Modular Monolith + Hexagonal + Event Driven + Plugin First"
        ),
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Attach Runtime to app state for lifespan access
    app.state.runtime = runtime
    app.state.settings = settings

    # Step 6 — CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Step 7 — Mount HTTP Adapters (routes)
    health_router = create_health_router(runtime=runtime)
    app.include_router(health_router)

    logger.info("FastAPI application configured", extra={"routes": len(app.routes)})

    return app


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "apps.runtime.src.bootstrap.main:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
        reload=settings.is_development,
    )
