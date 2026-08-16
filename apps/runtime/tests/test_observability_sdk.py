"""Tests for the shared observability contract and OTel adapter."""
from __future__ import annotations

import unittest

from apps.runtime.src.infrastructure.observability import OpenTelemetryObservability
from packages.shared.observability import NoopObservability


class ObservabilityTests(unittest.TestCase):
    def test_noop_span_and_metrics_are_safe(self) -> None:
        observability = NoopObservability()

        with observability.span("test.operation") as span:
            span.set_attribute("test.key", "value")
        observability.increment_counter("test.counter")
        observability.set_gauge("test.gauge", 1.0)

    def test_open_telemetry_adapter_without_exporter(self) -> None:
        observability = OpenTelemetryObservability(
            service_name="astera-test",
            enabled=True,
        )

        with observability.span("test.operation", {"test": True}) as span:
            span.set_attribute("test.key", "value")
        observability.increment_counter("test.counter")
        observability.set_gauge("test.gauge", 1.0)
        observability.shutdown()

