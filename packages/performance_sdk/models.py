"""Immutable latency and error summaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class OperationPerformance:
    operation: str
    sample_count: int
    error_count: int
    average_ms: float
    p50_ms: float
    p95_ms: float

    @property
    def error_rate(self) -> float:
        return self.error_count / self.sample_count if self.sample_count else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "sample_count": self.sample_count,
            "error_count": self.error_count,
            "error_rate": self.error_rate,
            "average_ms": self.average_ms,
            "p50_ms": self.p50_ms,
            "p95_ms": self.p95_ms,
        }


@dataclass(frozen=True, slots=True)
class PerformanceSnapshot:
    operations: tuple[OperationPerformance, ...]
    generated_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operations": [operation.to_dict() for operation in self.operations],
            "generated_at": self.generated_at.isoformat(),
        }
