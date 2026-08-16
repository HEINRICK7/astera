"""Bounded in-memory latency monitor."""
from __future__ import annotations

from collections import defaultdict, deque
from threading import RLock

from .models import OperationPerformance, PerformanceSnapshot


class InMemoryPerformanceMonitor:
    def __init__(self, *, max_samples_per_operation: int = 512) -> None:
        if max_samples_per_operation < 1:
            raise ValueError("max_samples_per_operation must be positive")
        self._max_samples = max_samples_per_operation
        self._samples: dict[str, deque[tuple[float, bool]]] = defaultdict(
            lambda: deque(maxlen=max_samples_per_operation)
        )
        self._lock = RLock()

    def record(self, operation: str, duration_ms: float, *, success: bool = True) -> None:
        if not operation.strip() or duration_ms < 0:
            raise ValueError("operation and duration must be valid")
        with self._lock:
            self._samples[operation].append((float(duration_ms), success))

    def snapshot(self) -> PerformanceSnapshot:
        with self._lock:
            summaries = []
            for operation, samples in sorted(self._samples.items()):
                durations = sorted(sample[0] for sample in samples)
                errors = sum(not sample[1] for sample in samples)
                summaries.append(
                    OperationPerformance(
                        operation=operation,
                        sample_count=len(durations),
                        error_count=errors,
                        average_ms=sum(durations) / len(durations),
                        p50_ms=self._percentile(durations, 0.50),
                        p95_ms=self._percentile(durations, 0.95),
                    )
                )
            return PerformanceSnapshot(operations=tuple(summaries))

    @staticmethod
    def _percentile(values: list[float], quantile: float) -> float:
        index = max(0, min(len(values) - 1, int((len(values) - 1) * quantile + 0.999999)))
        return values[index]
