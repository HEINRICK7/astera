"""Deterministic terminology provider for contract tests."""
from __future__ import annotations

from .models import TerminologyConcept, TerminologyQuery, TerminologyResult


class DeterministicTerminologyService:
    """Lookup configured concepts without requiring Snowstorm or LOINC services."""

    def __init__(
        self,
        concepts: tuple[TerminologyConcept, ...],
        *,
        provider: str = "deterministic",
    ) -> None:
        self._concepts = concepts
        self._provider = provider

    async def lookup(self, query: TerminologyQuery) -> TerminologyResult:
        matches = tuple(
            concept
            for concept in self._concepts
            if concept.system == query.system
            and (query.version is None or concept.version == query.version)
            and (
                query.code is not None
                and concept.code == query.code
                or query.text is not None
                and query.text.lower() in concept.display.lower()
            )
        )
        return TerminologyResult(query=query, provider=self._provider, concepts=matches)
