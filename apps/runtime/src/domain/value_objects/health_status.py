"""HealthStatus — health state for any platform component or provider."""
from __future__ import annotations

from enum import Enum


class HealthStatus(str, Enum):
    """Health status for any platform component, provider, or capability."""

    HEALTHY   = "healthy"
    DEGRADED  = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN   = "unknown"

    def is_ok(self) -> bool:
        return self == HealthStatus.HEALTHY

    def needs_attention(self) -> bool:
        return self in {HealthStatus.DEGRADED, HealthStatus.UNHEALTHY}
