"""Stable knowledge-state facade, separate from the main flow controller."""
from __future__ import annotations

from packages.clinical_facts_sdk import ClinicalFactsBatch

from apps.runtime.src.application.clinical.knowledge_layer import KnowledgeProjection
from .correlation import ClinicalCorrelationModule


class ClinicalKnowledgeModule:
    def __init__(self, correlation: ClinicalCorrelationModule) -> None:
        self._correlation = correlation

    @property
    def facts(self):
        return self._correlation.facts

    def apply(self, batch: ClinicalFactsBatch, *, source: str) -> KnowledgeProjection:
        return self._correlation.apply(batch, source=source)
