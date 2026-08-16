"""Deterministic correlation-to-understanding adapter."""
from __future__ import annotations

import hashlib

from packages.correlation_sdk import CorrelationBatch
from packages.evidence_sdk import EvidenceBatch

from .models import UnderstandingSnapshot, UnderstandingStatement


class CorrelationUnderstandingEngine:
    """Represent correlations as reviewable, evidence-backed statements."""

    async def build(
        self,
        *,
        evidence: EvidenceBatch,
        correlations: CorrelationBatch,
    ) -> UnderstandingSnapshot:
        statements = tuple(
            UnderstandingStatement(
                statement_id=hashlib.sha256(correlation.correlation_id.encode()).hexdigest()[:16],
                text=(
                    f"Evidence {', '.join(correlation.evidence_ids)} is related by "
                    f"{correlation.relation_type}."
                ),
                evidence_ids=correlation.evidence_ids,
                correlation_ids=(correlation.correlation_id,),
                confidence=correlation.confidence,
                metadata={"rationale": correlation.rationale},
            )
            for correlation in correlations.correlations
        )
        return UnderstandingSnapshot(
            encounter_id=evidence.encounter_id,
            statements=statements,
            status="draft",
        )
