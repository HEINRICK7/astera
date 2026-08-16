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

from packages.shared.config import ConfigurationLoader


class AsteraSettings(BaseSettings):
    """
    Central configuration for the Astera Runtime.

    All values are loaded from environment variables or the .env file.
    Variable names are prefixed with ASTERA_ to avoid conflicts.
    """

    model_config = {
        "env_prefix": "ASTERA_",
        "env_file": ".env",
        "case_sensitive": False,
        # Speech ownership moved out of Astera. Old deployment environments
        # may still contain ASTERA_* speech variables; they must not prevent
        # the clinical Runtime from starting after that ownership change.
        "extra": "ignore",
    }

    # ── Runtime ───────────────────────────────────────────────────────────────
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment.",
    )
    cognitive_provider: Literal["deterministic", "grok"] = Field(
        default="deterministic",
        description="Clinical NLP and reasoning provider profile.",
    )
    xai_api_key: str | None = Field(
        default=None,
        description="xAI API key. Set ASTERA_XAI_API_KEY outside source control.",
    )
    xai_base_url: str = Field(default="https://api.x.ai/v1")
    xai_model: str = Field(default="grok-4.5")
    xai_timeout_seconds: float = Field(default=180.0, gt=0)
    debug: bool = Field(default=False, description="Enable debug mode.")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Structured log level.",
    )

    # ── API ───────────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0", description="FastAPI host.")
    api_port: int = Field(default=8000, description="FastAPI port.", ge=1, le=65535)
    api_workers: int = Field(default=1, description="Number of Uvicorn workers.", ge=1)

    # ── Authentication ──────────────────────────────────────────────────────
    auth_secret: str = Field(
        default="astera-development-secret-change-in-production",
        min_length=32,
        description="JWT signing secret; override with ASTERA_AUTH_SECRET.",
    )
    auth_access_ttl_seconds: int = Field(
        default=900,
        description="JWT access token lifetime.",
        ge=60,
    )

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
    nats_startup_retries: int = Field(
        default=3,
        description="Bounded startup connection attempts before boot fails.",
        ge=1,
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
    redis_session_ttl_seconds: int = Field(
        default=3600,
        description="TTL for resumable clinical session state.",
        ge=1,
    )

    # ── Object Storage ───────────────────────────────────────────────────────
    minio_endpoint: str = Field(
        default="http://localhost:9000",
        description="S3-compatible object storage endpoint.",
    )
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    minio_bucket: str = Field(default="astera-evidence")
    minio_secure: bool = Field(default=False)

    # ── PostgreSQL recovery ────────────────────────────────────────────────
    postgres_dump_binary: str = Field(default="pg_dump")
    postgres_restore_binary: str = Field(default="pg_restore")
    postgres_backup_timeout_seconds: int = Field(default=300, ge=1)

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
    dependency_startup_retries: int = Field(
        default=3,
        description="Attempts for critical dependency readiness during startup.",
        ge=1,
    )
    dependency_retry_backoff_seconds: float = Field(
        default=0.25,
        description="Initial exponential backoff for dependency startup checks.",
        ge=0,
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
    return ConfigurationLoader(AsteraSettings).load()
