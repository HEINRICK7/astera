"""No-op observability implementation for disabled or isolated environments."""
from __future__ import annotations

from contextlib import nullcontext
from typing import Any

from packages.shared.observability.port import ObservabilityPort, SpanPort


class _NoopSpan:
    def set_attribute(self, key: str, value: Any) -> None:
        del key, value

    def record_exception(self, exception: BaseException) -> None:
        del exception


class NoopObservability:
    """Safe implementation that emits no telemetry."""

    def span(self, name: str, attributes: dict[str, Any] | None = None):
        del name, attributes
        return nullcontext(_NoopSpan())

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        del name, value, attributes

    def set_gauge(
        self,
        name: str,
        value: float,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        del name, value, attributes

