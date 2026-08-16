"""Deterministic Clinical Context builder for contract tests."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from packages.clinical_facts_sdk import ClinicalFactsBatch

from .models import ClinicalContext


class DeterministicClinicalContextBuilder:
    """Append facts to a versioned context while preserving prior state."""

    async def build(
        self,
        *,
        facts: ClinicalFactsBatch,
        previous: ClinicalContext | None = None,
        occurred_at: datetime | None = None,
    ) -> ClinicalContext:
        if previous is not None and previous.encounter_id != facts.encounter_id:
            raise ValueError("Clinical Context and Clinical Facts encounter must match")

        context_id = previous.context_id if previous else self._context_id(facts.encounter_id)
        patient_id = previous.patient_id if previous else self._patient_id(facts)
        if previous is not None and any(fact.subject_id != patient_id for fact in facts.items):
            raise ValueError("Clinical Facts subject must match the existing context patient")

        known = {fact.fact_id for fact in previous.facts} if previous else set()
        new_facts = tuple(fact for fact in facts.items if fact.fact_id not in known)
        timestamp = occurred_at or datetime.now(timezone.utc)
        previous_timeline = previous.timeline if previous else ()
        additions = tuple(
            {
                "event_type": "clinical.fact.detected",
                "fact_id": fact.fact_id,
                "occurred_at": fact.observed_at.isoformat() if fact.observed_at else timestamp.isoformat(),
                "source": fact.source,
            }
            for fact in new_facts
        )
        return ClinicalContext(
            context_id=context_id,
            context_version=(previous.context_version + 1) if previous else 1,
            patient_id=patient_id,
            encounter_id=facts.encounter_id,
            facts=(previous.facts if previous else ()) + new_facts,
            relationships=previous.relationships if previous else (),
            timeline=previous_timeline + additions,
            hypotheses=previous.hypotheses if previous else (),
            information_gaps=previous.information_gaps if previous else (),
            knowledge_references=previous.knowledge_references if previous else (),
            recommendations=previous.recommendations if previous else (),
            provenance={
                "builder": "deterministic-context-builder",
                "source_encounter": facts.encounter_id,
            },
            metadata=previous.metadata if previous else {},
            status="growing",
        )

    @staticmethod
    def _context_id(encounter_id: str) -> str:
        digest = hashlib.sha256(encounter_id.encode()).hexdigest()[:16]
        return f"context-{digest}"

    @staticmethod
    def _patient_id(facts: ClinicalFactsBatch) -> str:
        subjects = {fact.subject_id for fact in facts.items}
        if len(subjects) != 1:
            raise ValueError("Clinical Context requires one patient subject")
        return next(iter(subjects))
