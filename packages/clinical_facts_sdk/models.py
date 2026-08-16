"""Immutable contracts for provider-neutral Clinical Facts."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ClinicalMentionStatus(str, Enum):
    PARTIAL = "PARTIAL"
    FINAL = "FINAL"
    REVISED = "REVISED"
    DISCARDED = "DISCARDED"


@dataclass(frozen=True, slots=True)
class ClinicalMention:
    """A normalized, traceable clinical signal extracted from speech text.

    A mention is not a diagnosis and is not a Clinical Fact yet. It preserves
    the raw language and the normalization decision so downstream policy can
    review, reject, or promote it without rewriting the transcript.
    """

    id: str
    original_text: str
    normalized_text: str
    concept_id: str
    semantic_type: str
    confidence: float
    negated: bool
    temporality: str
    speaker: str
    provenance: Mapping[str, Any]
    certainty: str = "reported"
    segment_id: str = ""
    revision: int = 0
    status: ClinicalMentionStatus | str = ClinicalMentionStatus.FINAL
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)
    review_required: bool = False
    reported: bool = True
    ontology: str = "ASTERA-CONCEPT"
    code: str = ""
    semantic_value: int | float | str | None = None
    semantic_unit: str = ""
    segment_before: str = ""
    segment_current: str = ""
    segment_after: str = ""

    def __post_init__(self) -> None:
        required = (
            self.id,
            self.original_text,
            self.normalized_text,
            self.concept_id,
            self.semantic_type,
            self.temporality,
            self.speaker,
        )
        if any(not value.strip() for value in required):
            raise ValueError("Clinical Mention identity and semantic fields must not be empty")
        if not self.provenance:
            raise ValueError("Clinical Mention provenance must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.revision < 0:
            raise ValueError("revision must be zero or greater")
        if self.certainty not in {"confirmed", "suspected", "possible", "reported", "unknown"}:
            raise ValueError("unsupported Clinical Mention certainty")
        if self.temporality not in {"current", "past", "family_history", "future", "unknown"}:
            raise ValueError("unsupported Clinical Mention temporality")
        status_value = self.status.value if isinstance(self.status, ClinicalMentionStatus) else self.status
        if status_value not in {item.value for item in ClinicalMentionStatus}:
            raise ValueError("unsupported Clinical Mention status")

    @property
    def mention_id(self) -> str:
        """Stable domain name for the wire field required by SPR-002."""
        return self.id

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "mention_id": self.mention_id,
            "original_text": self.original_text,
            "normalized_text": self.normalized_text,
            "concept_id": self.concept_id,
            "semantic_type": self.semantic_type,
            "canonical": self.normalized_text,
            "confidence": self.confidence,
            "certainty": self.certainty,
            "status": self.status.value if isinstance(self.status, ClinicalMentionStatus) else self.status,
            "negated": self.negated,
            "reported": self.reported,
            "temporality": self.temporality,
            "speaker": self.speaker,
            "provenance": dict(self.provenance),
            "segment_id": self.segment_id,
            "revision": self.revision,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "review_required": self.review_required,
            "ontology": self.ontology,
            "code": self.code,
            "semantic_value": self.semantic_value,
            "semantic_unit": self.semantic_unit,
            "segment_before": self.segment_before,
            "segment_current": self.segment_current,
            "segment_after": self.segment_after,
        }


@dataclass(frozen=True, slots=True)
class ClinicalFact:
    """A traceable clinical fact candidate, not a diagnosis or recommendation."""

    fact_id: str
    category: str
    value: str
    subject_id: str
    encounter_id: str
    source: str
    provenance: Mapping[str, Any]
    patient_id: str | None = None
    unit: str | None = None
    confidence: float | None = None
    certainty: str = "reported"
    polarity: str = "positive"
    observed_at: datetime | None = None
    valid_at: datetime | None = None
    status: str = "candidate"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    canonical: str | None = None
    ontology: str | None = None
    code: str | None = None

    def __post_init__(self) -> None:
        required = (
            self.fact_id,
            self.category,
            self.value,
            self.subject_id,
            self.encounter_id,
            self.source,
            self.certainty,
            self.polarity,
            self.status,
        )
        if any(not value.strip() for value in required):
            raise ValueError("Clinical Fact identity and semantic fields must not be empty")
        if not self.provenance:
            raise ValueError("Clinical Fact provenance must not be empty")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        semantic_value = self.metadata.get("semantic_value")
        semantic_unit = self.metadata.get("semantic_unit") or self.unit
        return {
            "id": self.fact_id,
            "type": self.category.casefold(),
            "category": self.category,
            "value": semantic_value if semantic_value is not None else self.value,
            "display_value": self.value,
            "unit": semantic_unit,
            "subject": self.subject_id,
            "patient": self.patient_id,
            "encounter": self.encounter_id,
            "source": self.source,
            "provenance": dict(self.provenance),
            "confidence": self.confidence,
            "certainty": self.certainty,
            "polarity": self.polarity,
            "observed_at": self.observed_at.isoformat() if self.observed_at else None,
            "valid_at": self.valid_at.isoformat() if self.valid_at else None,
            "status": self.status,
            "metadata": dict(self.metadata),
            "canonical": self.canonical,
            "ontology": self.ontology,
            "code": self.code,
        }


@dataclass(frozen=True, slots=True)
class ClinicalFactsBatch:
    """A set of fact candidates belonging to one encounter."""

    encounter_id: str
    items: tuple[ClinicalFact, ...]

    def __post_init__(self) -> None:
        if not self.encounter_id.strip():
            raise ValueError("encounter_id must not be empty")
        if any(item.encounter_id != self.encounter_id for item in self.items):
            raise ValueError("all Clinical Facts must belong to the batch encounter")

    def to_dict(self) -> dict[str, Any]:
        return {
            "encounter_id": self.encounter_id,
            "items": [item.to_dict() for item in self.items],
        }
