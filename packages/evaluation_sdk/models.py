"""Immutable evaluation contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class EvaluationRequest:
    request_id: str
    input_text: str
    output_text: str
    reference_text: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("request_id must not be empty")
        if not self.input_text.strip() or not self.output_text.strip():
            raise ValueError("input_text and output_text must not be empty")


@dataclass(frozen=True, slots=True)
class MetricResult:
    name: str
    score: float
    passed: bool
    rationale: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.rationale.strip():
            raise ValueError("metric name and rationale must not be empty")
        if not 0 <= self.score <= 1:
            raise ValueError("score must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    request_id: str
    provider: str
    metrics: tuple[MetricResult, ...]

    @property
    def passed(self) -> bool:
        return bool(self.metrics) and all(metric.passed for metric in self.metrics)

    def to_dict(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "provider": self.provider,
            "passed": self.passed,
            "metrics": [
                {
                    "name": metric.name,
                    "score": metric.score,
                    "passed": metric.passed,
                    "rationale": metric.rationale,
                }
                for metric in self.metrics
            ],
        }
