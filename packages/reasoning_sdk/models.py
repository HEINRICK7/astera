"""Immutable contracts for the Clinical Reasoning Loop."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ClinicalHypothesis:
    """A provisional explanation, never a Clinical Fact or final diagnosis."""

    hypothesis_id: str
    name: str
    confidence: float
    supporting_facts: tuple[str, ...] = ()
    missing_facts: tuple[str, ...] = ()
    conflicting_facts: tuple[str, ...] = ()
    status: str = "candidate"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip() or not self.name.strip() or not self.status.strip():
            raise ValueError("hypothesis identity, name and status must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.hypothesis_id,
            "name": self.name,
            "confidence": self.confidence,
            "supporting_facts": list(self.supporting_facts),
            "missing_facts": list(self.missing_facts),
            "conflicting_facts": list(self.conflicting_facts),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True, slots=True)
class InformationGap:
    """Missing information that gives reasoning a traceable next question."""

    gap_id: str
    hypothesis_id: str
    missing_fact_type: str
    importance: str
    question: str
    acquisition_method: str
    status: str = "open"
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            self.gap_id,
            self.hypothesis_id,
            self.missing_fact_type,
            self.importance,
            self.question,
            self.acquisition_method,
            self.status,
        )
        if any(not value.strip() for value in required):
            raise ValueError("Information Gap fields must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.gap_id,
            "hypothesis_id": self.hypothesis_id,
            "missing_fact_type": self.missing_fact_type,
            "importance": self.importance,
            "question": self.question,
            "acquisition_method": self.acquisition_method,
            "status": self.status,
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True, slots=True)
class ClinicalQuestion:
    """A question justified by an Information Gap."""

    question_id: str
    text: str
    gap_id: str
    hypothesis_id: str
    objective: str
    status: str = "proposed"

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (
            self.question_id,
            self.text,
            self.gap_id,
            self.hypothesis_id,
            self.objective,
            self.status,
        )):
            raise ValueError("question fields must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.question_id,
            "text": self.text,
            "gap_id": self.gap_id,
            "hypothesis_id": self.hypothesis_id,
            "objective": self.objective,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class ClinicalReasoningResult:
    """One iteration of the Clinical Reasoning Loop."""

    encounter_id: str
    context_id: str
    context_version: int
    hypotheses: tuple[ClinicalHypothesis, ...]
    information_gaps: tuple[InformationGap, ...]
    questions: tuple[ClinicalQuestion, ...]
    cycle_status: str = "completed"

    def __post_init__(self) -> None:
        if not self.encounter_id.strip() or not self.context_id.strip():
            raise ValueError("reasoning context identity must not be empty")
        if self.context_version < 1 or not self.cycle_status.strip():
            raise ValueError("reasoning context version and cycle status are invalid")

    def to_dict(self) -> dict[str, Any]:
        return {
            "encounter_id": self.encounter_id,
            "context_id": self.context_id,
            "context_version": self.context_version,
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "information_gaps": [item.to_dict() for item in self.information_gaps],
            "questions": [item.to_dict() for item in self.questions],
            "cycle_status": self.cycle_status,
        }
