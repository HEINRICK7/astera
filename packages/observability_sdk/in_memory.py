"""Bounded in-memory operational telemetry for local runtime and tests."""
from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import RLock
from typing import Mapping
from uuid import uuid4

from .models import MetricPoint, OperationalEvent, ObservabilitySnapshot


class InMemoryOperationalObservability:
    """Store recent metrics and events without coupling the app to a vendor."""

    def __init__(self, *, max_events: int = 256) -> None:
        if max_events < 1:
            raise ValueError("max_events must be positive")
        self._lock = RLock()
        self._max_events = max_events
        self._metrics: dict[tuple[str, tuple[tuple[str, str], ...]], MetricPoint] = {}
        self._events: deque[OperationalEvent] = deque(maxlen=max_events)

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        attributes: Mapping[str, str] | None = None,
    ) -> None:
        if value < 0:
            raise ValueError("counter increment must not be negative")
        self._update_metric(name, "counter", float(value), attributes, accumulate=True)

    def set_gauge(
        self,
        name: str,
        value: float,
        attributes: Mapping[str, str] | None = None,
    ) -> None:
        self._update_metric(name, "gauge", float(value), attributes, accumulate=False)

    def record_event(
        self,
        name: str,
        *,
        severity: str = "info",
        attributes: Mapping[str, str] | None = None,
        trace_id: str | None = None,
    ) -> None:
        event = OperationalEvent(
            event_id=uuid4().hex,
            name=name,
            severity=severity,
            attributes=self._normalize_attributes(attributes),
            trace_id=trace_id,
            occurred_at=datetime.now(timezone.utc),
        )
        with self._lock:
            self._events.append(event)

    def snapshot(self) -> ObservabilitySnapshot:
        with self._lock:
            metrics = tuple(
                sorted(self._metrics.values(), key=lambda metric: (metric.name, metric.attributes))
            )
            return ObservabilitySnapshot(metrics=metrics, events=tuple(self._events))

    def _update_metric(
        self,
        name: str,
        kind: str,
        value: float,
        attributes: Mapping[str, str] | None,
        *,
        accumulate: bool,
    ) -> None:
        normalized = self._normalize_attributes(attributes)
        key = (name, normalized)
        with self._lock:
            previous = self._metrics.get(key)
            next_value = previous.value + value if accumulate and previous else value
            self._metrics[key] = MetricPoint(
                name=name,
                value=next_value,
                kind=kind,
                attributes=normalized,
                observed_at=datetime.now(timezone.utc),
            )

    @staticmethod
    def _normalize_attributes(attributes: Mapping[str, str] | None) -> tuple[tuple[str, str], ...]:
        return tuple(sorted((str(key), str(value)) for key, value in (attributes or {}).items()))
