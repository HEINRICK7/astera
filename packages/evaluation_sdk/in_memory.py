"""Deterministic evaluator for local contract tests."""
from __future__ import annotations

from .models import EvaluationRequest, EvaluationResult, MetricResult


class DeterministicEvaluator:
    """Evaluate response presence and optional exact reference agreement."""

    def __init__(self, *, provider: str = "deterministic", threshold: float = 1.0) -> None:
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self._provider = provider
        self._threshold = threshold

    async def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        metrics = [
            MetricResult(
                name="response_present",
                score=1.0 if request.output_text.strip() else 0.0,
                passed=bool(request.output_text.strip()),
                rationale="Output contains non-empty text.",
            )
        ]
        if request.reference_text is not None:
            score = 1.0 if request.output_text.strip() == request.reference_text.strip() else 0.0
            metrics.append(
                MetricResult(
                    name="reference_match",
                    score=score,
                    passed=score >= self._threshold,
                    rationale="Output matches the supplied reference." if score else "Output differs from the supplied reference.",
                )
            )
        return EvaluationResult(
            request_id=request.request_id,
            provider=self._provider,
            metrics=tuple(metrics),
        )
