"""Immutable evidence correlation contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Correlation:
    correlation_id: str
    encounter_id: str
    evidence_ids: tuple[str, ...]
    relation_type: str
    rationale: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.correlation_id.strip() or not self.encounter_id.strip():
            raise ValueError("correlation identity must not be empty")
        if len(self.evidence_ids) < 2:
            raise ValueError("a correlation must relate at least two evidence items")
        if not self.relation_type.strip() or not self.rationale.strip():
            raise ValueError("relation type and rationale must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "encounter_id": self.encounter_id,
            "evidence_ids": list(self.evidence_ids),
            "relation_type": self.relation_type,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class CorrelationBatch:
    encounter_id: str
    correlations: tuple[Correlation, ...]

    def __post_init__(self) -> None:
        if not self.encounter_id.strip():
            raise ValueError("encounter_id must not be empty")
        if any(item.encounter_id != self.encounter_id for item in self.correlations):
            raise ValueError("all correlations must belong to the batch encounter")

    def to_dict(self) -> dict[str, Any]:
        return {
            "encounter_id": self.encounter_id,
            "correlations": [item.to_dict() for item in self.correlations],
        }
