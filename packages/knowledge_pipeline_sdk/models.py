"""Immutable consolidated knowledge contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class KnowledgeRecord:
    record_id: str
    encounter_id: str
    version: str
    statements: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    correlation_ids: tuple[str, ...]
    status: str = "draft"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id.strip() or not self.encounter_id.strip() or not self.version.strip():
            raise ValueError("record identity and version must not be empty")
        if any(not statement.strip() for statement in self.statements):
            raise ValueError("statements must not contain empty values")
        if not self.status.strip():
            raise ValueError("status must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "encounter_id": self.encounter_id,
            "version": self.version,
            "statements": list(self.statements),
            "evidence_ids": list(self.evidence_ids),
            "correlation_ids": list(self.correlation_ids),
            "status": self.status,
            "metadata": dict(self.metadata),
        }
