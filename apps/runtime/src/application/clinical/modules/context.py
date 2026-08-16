"""Clinical context projection boundary."""
from __future__ import annotations

from datetime import datetime

from packages.clinical_context_sdk import ClinicalContext
from packages.clinical_facts_sdk import ClinicalFactsBatch, ClinicalFact

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextBuilderPort


class ClinicalContextModule:
    def __init__(self, builder: ClinicalContextBuilderPort) -> None:
        self._builder = builder

    async def build(
        self,
        *,
        facts: tuple[ClinicalFact, ...],
        encounter_id: str,
        previous: ClinicalContext | None,
        occurred_at: datetime,
    ) -> ClinicalContext:
        return await self._builder.build(
            facts=ClinicalFactsBatch(encounter_id=encounter_id, items=facts),
            previous=previous,
            occurred_at=occurred_at,
        )
