"""Medical NLP provider port."""
from __future__ import annotations

from typing import Protocol

from .models import NlpRequest, NlpResult


class MedicalNlpProcessor(Protocol):
    async def process(self, request: NlpRequest) -> NlpResult:
        """Extract structured text signals without clinical decision logic."""
