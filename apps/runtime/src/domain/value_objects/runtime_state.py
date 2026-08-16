"""RuntimeState — Kernel state machine."""
from __future__ import annotations

from enum import Enum


class RuntimeState(str, Enum):
    """
    Authoritative state machine for the AsteraKernel.

    Transitions:
        BOOTING  → READY    (bootstrap complete)
        BOOTING  → FAILED   (startup error)
        READY    → DEGRADED (component unhealthy)
        READY    → STOPPING (SIGTERM)
        DEGRADED → READY    (component recovered)
        DEGRADED → STOPPING (SIGTERM)
        STOPPING → STOPPED
        STOPPING → FAILED   (shutdown error)

    Read by: Grafana · Langfuse · Kubernetes probes · Health endpoints
    """

    BOOTING  = "booting"
    READY    = "ready"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED  = "stopped"
    FAILED   = "failed"

    def is_operational(self) -> bool:
        return self in {RuntimeState.READY, RuntimeState.DEGRADED}

    def is_healthy(self) -> bool:
        return self == RuntimeState.READY

    def is_terminal(self) -> bool:
        return self in {RuntimeState.STOPPED, RuntimeState.FAILED}

    def is_shutting_down(self) -> bool:
        return self in {RuntimeState.STOPPING, RuntimeState.STOPPED}

    def can_accept_plugins(self) -> bool:
        return self in {RuntimeState.BOOTING, RuntimeState.READY, RuntimeState.DEGRADED}
