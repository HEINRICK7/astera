"""OpenTelemetry adapter for the shared observability port."""
from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import Counter, MeterProvider, UpDownCounter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from packages.shared.observability import NoopObservability, ObservabilityPort, SpanPort


class _OpenTelemetrySpan(AbstractContextManager[SpanPort]):
    def __init__(self, tracer: Any, name: str, attributes: dict[str, Any] | None) -> None:
        self._context = tracer.start_as_current_span(name, attributes=attributes or {})
        self._span: Any = None

    def __enter__(self) -> SpanPort:
        self._span = self._context.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        if exc_value is not None:
            self.record_exception(exc_value)
        return self._context.__exit__(exc_type, exc_value, traceback)

    def set_attribute(self, key: str, value: Any) -> None:
        self._span.set_attribute(key, value)

    def record_exception(self, exception: BaseException) -> None:
        self._span.record_exception(exception)


class OpenTelemetryObservability:
    """OpenTelemetry implementation with optional OTLP gRPC exporters."""

    def __init__(
        self,
        service_name: str,
        endpoint: str | None = None,
        enabled: bool = True,
    ) -> None:
        self._noop: ObservabilityPort | None = None
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, UpDownCounter] = {}
        if not enabled:
            self._noop = NoopObservability()
            return

        resource = Resource.create({"service.name": service_name})
        self._tracer_provider = TracerProvider(resource=resource)
        self._meter_provider = MeterProvider(resource=resource)
        if endpoint:
            self._tracer_provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
            )
            self._meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[
                    PeriodicExportingMetricReader(
                        OTLPMetricExporter(endpoint=endpoint, insecure=True)
                    )
                ],
            )
        self._tracer = self._tracer_provider.get_tracer("astera.runtime")
        self._meter = self._meter_provider.get_meter("astera.runtime")

    def span(self, name: str, attributes: dict[str, Any] | None = None):
        if self._noop:
            return self._noop.span(name, attributes)
        return _OpenTelemetrySpan(self._tracer, name, attributes)

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        if self._noop:
            self._noop.increment_counter(name, value, attributes)
            return
        counter = self._counters.setdefault(name, self._meter.create_counter(name))
        counter.add(value, attributes=attributes or {})

    def set_gauge(
        self,
        name: str,
        value: float,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        if self._noop:
            self._noop.set_gauge(name, value, attributes)
            return
        gauge = self._gauges.setdefault(name, self._meter.create_up_down_counter(name))
        gauge.add(value, attributes=attributes or {})

    def shutdown(self) -> None:
        if self._noop:
            return
        self._meter_provider.shutdown()
        self._tracer_provider.shutdown()


def create_observability(
    service_name: str,
    endpoint: str,
    enabled: bool,
) -> OpenTelemetryObservability:
    """Create the configured runtime adapter."""
    return OpenTelemetryObservability(service_name, endpoint, enabled)

