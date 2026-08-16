"""Correlation boundary for relationships among canonical facts."""
from __future__ import annotations

from packages.clinical_facts_sdk import ClinicalFactsBatch

from apps.runtime.src.application.clinical.knowledge_layer import ClinicalKnowledgeLayer, KnowledgeProjection


class ClinicalCorrelationModule:
    """Apply fact changes to the correlation/knowledge projection."""

    def __init__(self) -> None:
        self._knowledge = ClinicalKnowledgeLayer()

    @property
    def facts(self):
        return self._knowledge.facts

    def apply(self, batch: ClinicalFactsBatch, *, source: str) -> KnowledgeProjection:
        return self._knowledge.apply(batch, source=source)
