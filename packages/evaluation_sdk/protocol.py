"""Evaluation provider port."""
from __future__ import annotations

from typing import Protocol

from .models import EvaluationRequest, EvaluationResult


class Evaluator(Protocol):
    async def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """Evaluate a response without exposing framework-specific APIs."""
