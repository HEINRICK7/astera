"""Immutable understanding contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class UnderstandingStatement:
    statement_id: str
    text: str
    evidence_ids: tuple[str, ...]
    correlation_ids: tuple[str, ...]
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.statement_id.strip() or not self.text.strip():
            raise ValueError("statement identity and text must not be empty")
        if not self.evidence_ids:
            raise ValueError("statement must reference evidence")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement_id": self.statement_id,
            "text": self.text,
            "evidence_ids": list(self.evidence_ids),
            "correlation_ids": list(self.correlation_ids),
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class UnderstandingSnapshot:
    encounter_id: str
    statements: tuple[UnderstandingStatement, ...]
    status: str = "draft"

    def __post_init__(self) -> None:
        if not self.encounter_id.strip() or not self.status.strip():
            raise ValueError("encounter_id and status must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "encounter_id": self.encounter_id,
            "status": self.status,
            "statements": [statement.to_dict() for statement in self.statements],
        }
