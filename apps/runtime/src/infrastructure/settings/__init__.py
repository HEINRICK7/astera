"""
Astera Runtime — Infrastructure Settings.

All configuration is loaded via Pydantic Settings from environment variables.
No hardcoded values. No configuration files committed with secrets.

Usage:
    from apps.runtime.src.infrastructure.settings import get_settings
    settings = get_settings()
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class AsteraSettings(BaseSettings):
    """
    Central configuration for the Astera Runtime.

    All values are loaded from environment variables or the .env file.
    Variable names are prefixed with ASTERA_ to avoid conflicts.
    """

    model_config = {"env_prefix": "ASTERA_", "env_file": ".env", "case_sensitive": False}

    # ── Runtime ───────────────────────────────────────────────────────────────
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment.",
    )
    debug: bool = Field(default=False, description="Enable debug mode.")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Structured log level.",
    )

    # ── API ───────────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0", description="FastAPI host.")
    api_port: int = Field(default=8000, description="FastAPI port.", ge=1, le=65535)
    api_workers: int = Field(default=1, description="Number of Uvicorn workers.", ge=1)

    # ── NATS / Event Bus ──────────────────────────────────────────────────────
    nats_url: str = Field(
        default="nats://localhost:4222",
        description="NATS server URL for the Event Bus.",
    )
    nats_connect_timeout: float = Field(
        default=5.0,
        description="NATS connection timeout in seconds.",
        ge=0.1,
    )
    nats_reconnect_time_wait: float = Field(
        default=2.0,
        description="NATS reconnection wait time in seconds.",
        ge=0.1,
    )
    nats_max_reconnect_attempts: int = Field(
        default=10,
        description="Maximum NATS reconnection attempts. -1 for infinite.",
    )

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    postgres_url: str = Field(
        default="postgresql+asyncpg://astera:astera@localhost:5432/astera",
        description="PostgreSQL async connection URL.",
    )

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL.",
    )

    # ── Observability ─────────────────────────────────────────────────────────
    otel_endpoint: str = Field(
        default="http://localhost:4317",
        description="OpenTelemetry Collector gRPC endpoint.",
    )
    otel_service_name: str = Field(
        default="astera-runtime",
        description="Service name reported to OpenTelemetry.",
    )
    otel_enabled: bool = Field(
        default=True,
        description="Enable OpenTelemetry instrumentation.",
    )

    # ── Health ────────────────────────────────────────────────────────────────
    health_check_interval_seconds: int = Field(
        default=30,
        description="Interval between internal health checks in seconds.",
        ge=5,
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache(maxsize=1)
def get_settings() -> AsteraSettings:
    """
    Return a cached singleton of AsteraSettings.

    The cache ensures settings are loaded only once per process lifetime.
    In tests, call get_settings.cache_clear() before overriding env vars.
    """
    return AsteraSettings()
