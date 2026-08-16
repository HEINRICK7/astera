"""Deterministic Understanding-to-Knowledge adapter."""
from __future__ import annotations

from hashlib import sha256

from packages.understanding_sdk import UnderstandingSnapshot

from .models import KnowledgeRecord


class SnapshotKnowledgeEngine:
    """Consolidate a draft snapshot without creating a clinical representation."""

    async def consolidate(self, snapshot: UnderstandingSnapshot) -> KnowledgeRecord:
        evidence_ids = tuple(
            sorted({evidence_id for statement in snapshot.statements for evidence_id in statement.evidence_ids})
        )
        correlation_ids = tuple(
            sorted({correlation_id for statement in snapshot.statements for correlation_id in statement.correlation_ids})
        )
        record_id = sha256(snapshot.encounter_id.encode()).hexdigest()[:16]
        return KnowledgeRecord(
            record_id=record_id,
            encounter_id=snapshot.encounter_id,
            version="1",
            statements=tuple(statement.text for statement in snapshot.statements),
            evidence_ids=evidence_ids,
            correlation_ids=correlation_ids,
            status="draft",
        )
