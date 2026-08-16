"""Understanding engine port."""
from __future__ import annotations

from typing import Protocol

from packages.correlation_sdk import CorrelationBatch
from packages.evidence_sdk import EvidenceBatch

from .models import UnderstandingSnapshot


class UnderstandingEngine(Protocol):
    async def build(
        self,
        *,
        evidence: EvidenceBatch,
        correlations: CorrelationBatch,
    ) -> UnderstandingSnapshot:
        """Build a provisional understanding without making clinical decisions."""
