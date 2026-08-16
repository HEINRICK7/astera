"""Shared observability contract used by application modules."""
from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol


class SpanPort(Protocol):
    """Minimal span operations exposed to the application layer."""

    def set_attribute(self, key: str, value: Any) -> None:
        ...

    def record_exception(self, exception: BaseException) -> None:
        ...


class ObservabilityPort(Protocol):
    """Tracing and metrics port independent of OpenTelemetry internals."""

    def span(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> AbstractContextManager[SpanPort]:
        ...

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        ...

    def set_gauge(
        self,
        name: str,
        value: float,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        ...
