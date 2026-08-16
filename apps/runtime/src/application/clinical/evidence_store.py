"""Stable clinical evidence state between normalization and knowledge."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any

from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsBatch


@dataclass(frozen=True, slots=True)
class EvidenceEvent:
    event_id: str
    encounter_id: str
    source: str
    fact_id: str
    category: str
    value: str
    lifecycle: str
    occurred_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "encounter_id": self.encounter_id,
            "source": self.source,
            "event_type": "clinical.evidence.upserted",
            "fact_id": self.fact_id,
            "category": self.category,
            "value": self.value,
            "lifecycle": self.lifecycle,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class EvidenceProjection:
    version: int
    facts: tuple[ClinicalFact, ...]
    events: tuple[EvidenceEvent, ...]
    timeline: tuple[dict[str, Any], ...]
    history: tuple[dict[str, Any], ...]
    lifecycles: dict[str, str]


class EvidenceStore:
    """Upsert facts into one stable evidence state per encounter."""

    def __init__(self) -> None:
        self._facts: dict[str, ClinicalFact] = {}
        self._semantic_ids: dict[tuple[str, str, str, str], str] = {}
        self._lifecycles: dict[str, str] = {}
        self._timeline: dict[str, dict[str, Any]] = {}
        self._history: list[dict[str, Any]] = []
        self._version = 0

    @property
    def facts(self) -> tuple[ClinicalFact, ...]:
        return tuple(self._facts.values())

    def apply(self, batch: ClinicalFactsBatch, *, source: str) -> EvidenceProjection:
        if any(fact.encounter_id != batch.encounter_id for fact in batch.items):
            raise ValueError("Evidence Facts must belong to the projection encounter")

        occurred_at = datetime.now(timezone.utc)
        events: list[EvidenceEvent] = []
        for fact in batch.items:
            semantic_identity = fact.code or str(fact.metadata.get("concept_id", "")) or f"{fact.category}:{fact.value}"
            key = (fact.subject_id, semantic_identity.casefold(), fact.polarity, fact.encounter_id)
            existing_id = self._semantic_ids.get(key)
            if existing_id is None:
                fact_id = fact.fact_id
                self._semantic_ids[key] = fact_id
                self._facts[fact_id] = fact
                self._lifecycles[fact_id] = "created"
                lifecycle = "created"
            else:
                fact_id = existing_id
                previous = self._facts[existing_id]
                self._facts[existing_id] = self._merge(previous, fact, existing_id)
                self._lifecycles[fact_id] = "growing"
                lifecycle = "growing"

            event_id = f"evidence-{batch.encounter_id}-{self._version + len(events) + 1}"
            current = self._facts[fact_id]
            evidence_event = EvidenceEvent(
                event_id=event_id,
                encounter_id=batch.encounter_id,
                source=source,
                fact_id=fact_id,
                category=current.category,
                value=current.value,
                lifecycle=lifecycle,
                occurred_at=occurred_at,
            )
            events.append(evidence_event)
            previous_timeline = self._timeline.get(fact_id)
            timeline_entry: dict[str, Any] = {
                "timeline_id": event_id,
                "event_type": "clinical.evidence.upserted",
                "category": current.category,
                "value": current.value,
                "fact_id": fact_id,
                "lifecycle": lifecycle,
                "source": source,
                "occurred_at": occurred_at.isoformat(),
                "update_count": (previous_timeline or {}).get("update_count", 0) + 1,
            }
            if previous_timeline and previous_timeline.get("value") != current.value:
                timeline_entry["previous_value"] = previous_timeline["value"]
            self._timeline[fact_id] = timeline_entry
            self._history.append({**timeline_entry, "update_kind": lifecycle})

        if batch.items:
            self._version += 1
        return EvidenceProjection(
            version=self._version,
            facts=self.facts,
            events=tuple(events),
            timeline=tuple(self._timeline.values()),
            history=tuple(self._history),
            lifecycles=dict(self._lifecycles),
        )

    @staticmethod
    def _merge(previous: ClinicalFact, incoming: ClinicalFact, fact_id: str) -> ClinicalFact:
        provenance = {
            **dict(previous.provenance),
            **dict(incoming.provenance),
            "source_refs": tuple(dict.fromkeys(
                (
                    *previous.provenance.get("source_refs", ()),
                    previous.provenance.get("source_ref"),
                    *incoming.provenance.get("source_refs", ()),
                    incoming.provenance.get("source_ref"),
                )
            )),
        }
        metadata = {**dict(previous.metadata), **dict(incoming.metadata)}
        return replace(
            previous,
            fact_id=fact_id,
            category=incoming.category,
            value=incoming.value,
            unit=incoming.unit or previous.unit,
            provenance={key: value for key, value in provenance.items() if value is not None},
            confidence=max(previous.confidence or 0, incoming.confidence or 0) or None,
            certainty=incoming.certainty,
            observed_at=incoming.observed_at or previous.observed_at,
            valid_at=incoming.valid_at or previous.valid_at,
            status=incoming.status,
            metadata=metadata,
            canonical=incoming.canonical or previous.canonical,
            ontology=incoming.ontology or previous.ontology,
            code=incoming.code or previous.code,
        )
