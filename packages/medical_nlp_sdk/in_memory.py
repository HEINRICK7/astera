"""Deterministic local Medical NLP processor for contract tests."""
from __future__ import annotations

from .models import ClinicalEntity, NlpRequest, NlpResult


class DeterministicMedicalNlp:
    """Return configured entities while preserving provider boundaries."""

    def __init__(self, entities: tuple[ClinicalEntity, ...], *, provider: str = "deterministic") -> None:
        self._entities = entities
        self._provider = provider

    async def process(self, request: NlpRequest) -> NlpResult:
        return NlpResult(
            request_id=request.request_id,
            provider=self._provider,
            entities=self._entities,
            language=request.language,
        )
