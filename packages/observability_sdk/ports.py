"""Ports for enterprise operational observability."""
from __future__ import annotations

from typing import Mapping, Protocol

from .models import ObservabilitySnapshot


class OperationalObservabilityPort(Protocol):
    """Application-facing operational telemetry port."""

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        attributes: Mapping[str, str] | None = None,
    ) -> None:
        ...

    def set_gauge(
        self,
        name: str,
        value: float,
        attributes: Mapping[str, str] | None = None,
    ) -> None:
        ...

    def record_event(
        self,
        name: str,
        *,
        severity: str = "info",
        attributes: Mapping[str, str] | None = None,
        trace_id: str | None = None,
    ) -> None:
        ...

    def snapshot(self) -> ObservabilitySnapshot:
        ...
