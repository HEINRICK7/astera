"""Clinical Context builder port."""
from __future__ import annotations

from datetime import datetime
from typing import Protocol

from packages.clinical_facts_sdk import ClinicalFactsBatch

from .models import ClinicalContext


class ClinicalContextBuilder(Protocol):
    async def build(
        self,
        *,
        facts: ClinicalFactsBatch,
        previous: ClinicalContext | None = None,
        occurred_at: datetime | None = None,
    ) -> ClinicalContext:
        """Create or version a Clinical Context without clinical reasoning."""
