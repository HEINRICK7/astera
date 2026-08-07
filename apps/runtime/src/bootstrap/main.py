"""
Astera Runtime — Platform Bootstrap (Kernel Edition).

Entry point of the Astera platform. Wires all components together
and hands control to the AsteraKernel.

Bootstrap sequence:
    1. Configure Logging
    2. Load Configuration (AsteraSettings)
    3. Build Dependency Container (concrete adapters)
    4. Create AsteraKernel (the platform OS)
    5. Configure FastAPI (routes, middleware)
    6. Start Kernel (via FastAPI lifespan)
    7. API accepts traffic when Kernel state == READY

Run:
    python -m apps.runtime.src.bootstrap.main
    uvicorn apps.runtime.src.bootstrap.main:create_app --factory
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Infrastructure ────────────────────────────────────────────────────────────
from apps.runtime.src.infrastructure.settings import get_settings
from apps.runtime.src.infrastructure.logging import configure_logging

# ── Adapters (only place concrete implementations are instantiated) ────────────
from apps.runtime.src.adapters.nats import NatsEventBusAdapter
from apps.runtime.src.adapters.http.health import create_health_router

# ── Kernel ────────────────────────────────────────────────────────────────────
from apps.runtime.src.application.kernel import AsteraKernel

logger = logging.getLogger("astera.bootstrap")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.

    Delegates entirely to AsteraKernel.startup() and AsteraKernel.shutdown().
    The API is NOT available until the Kernel reaches READY state.
    """
    kernel: AsteraKernel = app.state.kernel

    try:
        await kernel.startup()
    except Exception as exc:
        logger.critical("Platform Bootstrap FAILED", extra={"error": str(exc)}, exc_info=True)
        raise SystemExit(1) from exc

    yield  # ← Kernel is READY. API accepts traffic.

    await kernel.shutdown()


# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    Astera Platform application factory.

    Wiring order:
        Settings → Logging → Adapters → Kernel → FastAPI → Routes
    """
    # 1. Configuration
    settings = get_settings()

    # 2. Logging (must be first log consumer)
    configure_logging(
        level=settings.log_level,
        json_format=settings.is_production,
    )

    logger.info(
        "Bootstrapping Astera Platform",
        extra={
            "environment": settings.environment,
            "version": "0.1.0",
        },
    )

    # 3. Dependency Container — wire concrete → abstract
    event_bus = NatsEventBusAdapter(
        nats_url=settings.nats_url,
        connect_timeout=settings.nats_connect_timeout,
    )

    # 4. Kernel (the platform OS)
    kernel = AsteraKernel(event_bus=event_bus)

    # 5. FastAPI application
    app = FastAPI(
        title="Astera Runtime",
        description=(
            "**Astera Platform Kernel** — the operating system of the Astera clinical intelligence platform.\n\n"
            "All platform capabilities (Speech, Vision, OCR, Medical NLP, Google ADK) "
            "exist as extensions registered in this Kernel.\n\n"
            "**Architecture:** Modular Monolith · Hexagonal · Event Driven · Plugin First\n\n"
            "**ADR-001:** Modular Monolith — not microservices."
        ),
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Attach Kernel to app state (accessed in lifespan)
    app.state.kernel = kernel
    app.state.settings = settings

    # 6. Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 7. Routes — inject Kernel as KernelPort (depends on interface, not implementation)
    app.include_router(create_health_router(kernel=kernel))

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
