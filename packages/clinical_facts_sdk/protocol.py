"""Clinical Facts extraction port."""
from __future__ import annotations

from datetime import datetime
from typing import Protocol

from packages.medical_nlp_sdk import NlpResult

from .models import ClinicalFactsBatch, ClinicalMention


class ClinicalFactsExtractor(Protocol):
    async def extract(
        self,
        *,
        encounter_id: str,
        subject_id: str,
        patient_id: str | None,
        result: NlpResult | None = None,
        mentions: tuple[ClinicalMention, ...] = (),
        observed_at: datetime | None = None,
    ) -> ClinicalFactsBatch:
        """Convert structured NLP signals into traceable Clinical Facts."""
