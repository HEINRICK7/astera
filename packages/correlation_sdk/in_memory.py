"""Deterministic shared-term correlation engine."""
from __future__ import annotations

import hashlib
import re
from itertools import combinations

from packages.evidence_sdk import EvidenceBatch

from .models import Correlation, CorrelationBatch


class SharedTermCorrelationEngine:
    """Correlate evidence pairs that share meaningful terms."""

    async def correlate(self, batch: EvidenceBatch) -> CorrelationBatch:
        correlations: list[Correlation] = []
        for left, right in combinations(batch.items, 2):
            shared = _terms(left.content) & _terms(right.content)
            if not shared:
                continue
            evidence_ids = tuple(sorted((left.evidence_id, right.evidence_id)))
            correlation_id = hashlib.sha256(":".join(evidence_ids).encode()).hexdigest()[:16]
            correlations.append(
                Correlation(
                    correlation_id=correlation_id,
                    encounter_id=batch.encounter_id,
                    evidence_ids=evidence_ids,
                    relation_type="shared_term",
                    rationale=f"Shared terms: {', '.join(sorted(shared))}",
                    confidence=min(1.0, len(shared) / max(len(_terms(left.content)), 1)),
                    metadata={"shared_terms": sorted(shared)},
                )
            )
        return CorrelationBatch(encounter_id=batch.encounter_id, correlations=tuple(correlations))


def _terms(text: str) -> set[str]:
    return {term.lower() for term in re.findall(r"[\wÀ-ÿ]+", text) if len(term) > 2}
