"""Evidence extraction port."""
from __future__ import annotations

from typing import Protocol

from packages.contracts.transcription import Transcript

from .models import EvidenceBatch


class EvidenceExtractor(Protocol):
    async def extract(self, *, encounter_id: str, transcript: Transcript) -> EvidenceBatch:
        """Convert observations into traceable evidence without interpretation."""
