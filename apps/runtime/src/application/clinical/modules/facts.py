"""Clinical fact extraction boundary."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsBatch, ClinicalFactsExtractor
from packages.clinical_facts_sdk import ClinicalMention


class ClinicalFactsModule:
    def __init__(self, extractor: ClinicalFactsExtractor) -> None:
        self._extractor = extractor

    async def extract(
        self,
        *,
        encounter_id: str,
        subject_id: str,
        patient_id: str,
        mentions: Iterable[ClinicalMention],
        observed_at: datetime,
    ) -> ClinicalFactsBatch:
        return await self._extractor.extract(
            encounter_id=encounter_id,
            subject_id=subject_id,
            patient_id=patient_id,
            mentions=tuple(mentions),
            observed_at=observed_at,
        )

    @staticmethod
    def empty(encounter_id: str) -> ClinicalFactsBatch:
        return ClinicalFactsBatch(encounter_id=encounter_id, items=())
