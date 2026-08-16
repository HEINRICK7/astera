"""Immutable Clinical Context contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from packages.clinical_facts_sdk import ClinicalFact


@dataclass(frozen=True, slots=True)
class ClinicalContext:
    """Versioned clinical state derived from facts and their timeline."""

    context_id: str
    context_version: int
    patient_id: str
    encounter_id: str
    facts: tuple[ClinicalFact, ...] = ()
    relationships: tuple[Mapping[str, Any], ...] = ()
    timeline: tuple[Mapping[str, Any], ...] = ()
    hypotheses: tuple[Mapping[str, Any], ...] = ()
    information_gaps: tuple[Mapping[str, Any], ...] = ()
    knowledge_references: tuple[Mapping[str, Any], ...] = ()
    recommendations: tuple[Mapping[str, Any], ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    status: str = "growing"

    def __post_init__(self) -> None:
        required = (self.context_id, self.patient_id, self.encounter_id, self.status)
        if any(not value.strip() for value in required):
            raise ValueError("Clinical Context identity and status must not be empty")
        if self.context_version < 1:
            raise ValueError("context_version must be at least 1")
        if any(fact.encounter_id != self.encounter_id for fact in self.facts):
            raise ValueError("all Clinical Facts must belong to the context encounter")

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "context_version": self.context_version,
            "patient_id": self.patient_id,
            "encounter_id": self.encounter_id,
            "facts": [fact.to_dict() for fact in self.facts],
            "relationships": [dict(item) for item in self.relationships],
            "timeline": [dict(item) for item in self.timeline],
            "hypotheses": [dict(item) for item in self.hypotheses],
            "information_gaps": [dict(item) for item in self.information_gaps],
            "knowledge_references": [dict(item) for item in self.knowledge_references],
            "recommendations": [dict(item) for item in self.recommendations],
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
            "status": self.status,
        }


def parse_datetime(value: Any) -> datetime | None:
    """Parse context timestamps at the plugin boundary."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise TypeError("timestamp must be an ISO datetime string")
