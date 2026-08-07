"""
Astera Shared Models — Platform Enums.

Shared enumerations used across multiple packages.
Do not import package-specific enums here — keep this general.
"""
from __future__ import annotations

from enum import Enum


class ComponentStatus(str, Enum):
    """
    Status of any platform component, as reported to health checks and Grafana.

    Used in:
        - Health reports (/ready endpoint)
        - Grafana dashboards
        - NATS component.status events
    """

    HEALTHY   = "healthy"
    DEGRADED  = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING  = "starting"
    STOPPING  = "stopping"
    UNKNOWN   = "unknown"

    def is_ok(self) -> bool:
        return self == ComponentStatus.HEALTHY

    def needs_attention(self) -> bool:
        return self in {ComponentStatus.DEGRADED, ComponentStatus.UNHEALTHY}


class EventPriority(str, Enum):
    """
    Priority level for events published to the Event Bus.

    Future: the Event Bus adapter may use this to route
    high-priority events to dedicated NATS subjects.
    """

    LOW      = "low"
    NORMAL   = "normal"
    HIGH     = "high"
    CRITICAL = "critical"


class DataSensitivity(str, Enum):
    """
    Data sensitivity classification — used for LGPD compliance.

    Every ContextScope and clinical event carries this classification.
    The Security layer (Phase G) enforces encryption and access control
    based on this value.
    """

    PUBLIC       = "public"         # No patient data
    INTERNAL     = "internal"       # Internal platform data
    CONFIDENTIAL = "confidential"   # PHI — Protected Health Information
    RESTRICTED   = "restricted"     # Highly sensitive (mental health, HIV, etc.)
