"""Optional/deep clinical research boundary."""
from __future__ import annotations

from packages.clinical_context_sdk import ClinicalContext
from packages.reasoning_sdk import ClinicalReasoner, ClinicalReasoningResult


class ClinicalResearchModule:
    """Research/reasoning is invoked by the flow but does not own the flow."""

    def __init__(self, reasoner: ClinicalReasoner) -> None:
        self._reasoner = reasoner

    async def reason(self, context: ClinicalContext) -> ClinicalReasoningResult:
        return await self._reasoner.reason(context)
