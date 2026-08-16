"""Immutable evidence contracts derived from observations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_id: str
    encounter_id: str
    source_type: str
    content: str
    origin_id: str
    start_ms: int = 0
    end_ms: int = 0
    confidence: float | None = None
    speaker: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (self.evidence_id, self.encounter_id, self.source_type, self.content, self.origin_id)
        if any(not value.strip() for value in required):
            raise ValueError("evidence identity and content must not be empty")
        if self.start_ms < 0 or self.end_ms < self.start_ms:
            raise ValueError("evidence timestamps must be ordered")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "encounter_id": self.encounter_id,
            "source_type": self.source_type,
            "content": self.content,
            "origin_id": self.origin_id,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "confidence": self.confidence,
            "speaker": self.speaker,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class EvidenceBatch:
    encounter_id: str
    items: tuple[EvidenceItem, ...]

    def __post_init__(self) -> None:
        if not self.encounter_id.strip():
            raise ValueError("encounter_id must not be empty")
        if any(item.encounter_id != self.encounter_id for item in self.items):
            raise ValueError("all evidence must belong to the batch encounter")

    def to_dict(self) -> dict[str, Any]:
        return {
            "encounter_id": self.encounter_id,
            "items": [item.to_dict() for item in self.items],
        }
