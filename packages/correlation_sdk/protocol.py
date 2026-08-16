"""Correlation engine port."""
from __future__ import annotations

from typing import Protocol

from packages.evidence_sdk import EvidenceBatch

from .models import CorrelationBatch


class CorrelationEngine(Protocol):
    async def correlate(self, batch: EvidenceBatch) -> CorrelationBatch:
        """Identify explicit relations without making clinical decisions."""
