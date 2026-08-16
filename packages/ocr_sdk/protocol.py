"""OCR provider port."""
from __future__ import annotations

from typing import Protocol

from .models import OcrRequest, OcrResult


class OcrEngine(Protocol):
    async def extract(self, request: OcrRequest) -> OcrResult:
        """Extract text without exposing engine-specific APIs."""
