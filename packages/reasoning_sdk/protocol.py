"""Clinical Reasoning Loop provider port."""
from __future__ import annotations

from typing import Protocol

from packages.clinical_context_sdk import ClinicalContext

from .models import ClinicalReasoningResult


class ClinicalReasoner(Protocol):
    async def reason(self, context: ClinicalContext) -> ClinicalReasoningResult:
        """Generate competing hypotheses, gaps and traceable questions."""
