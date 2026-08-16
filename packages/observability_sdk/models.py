"""Immutable contracts for operational telemetry exposed by the platform."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _attributes_to_dict(attributes: tuple[tuple[str, str], ...]) -> dict[str, str]:
    return dict(attributes)


@dataclass(frozen=True, slots=True)
class MetricPoint:
    """Current value of a named operational metric."""

    name: str
    value: float
    kind: str
    attributes: tuple[tuple[str, str], ...] = ()
    observed_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("metric name must not be empty")
        if self.kind not in {"counter", "gauge"}:
            raise ValueError("metric kind must be counter or gauge")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "kind": self.kind,
            "attributes": _attributes_to_dict(self.attributes),
            "observed_at": self.observed_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class OperationalEvent:
    """Structured, non-sensitive event retained for operational diagnosis."""

    event_id: str
    name: str
    severity: str = "info"
    attributes: tuple[tuple[str, str], ...] = ()
    trace_id: str | None = None
    occurred_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if not self.event_id.strip() or not self.name.strip():
            raise ValueError("event identity fields must not be empty")
        if self.severity not in {"debug", "info", "warning", "error"}:
            raise ValueError("unsupported event severity")

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "name": self.name,
            "severity": self.severity,
            "attributes": _attributes_to_dict(self.attributes),
            "trace_id": self.trace_id,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ObservabilitySnapshot:
    """Point-in-time view used by operators and health tooling."""

    metrics: tuple[MetricPoint, ...]
    events: tuple[OperationalEvent, ...]
    generated_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": [metric.to_dict() for metric in self.metrics],
            "events": [event.to_dict() for event in self.events],
            "generated_at": self.generated_at.isoformat(),
        }
