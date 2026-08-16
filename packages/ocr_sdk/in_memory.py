"""Deterministic local OCR engine for contract tests."""
from __future__ import annotations

from .models import OcrBlock, OcrRequest, OcrResult


class DeterministicOcrEngine:
    """Return configured OCR blocks while preserving the provider boundary."""

    def __init__(self, blocks: tuple[OcrBlock, ...], *, provider: str = "deterministic") -> None:
        if not blocks:
            raise ValueError("blocks must not be empty")
        self._blocks = blocks
        self._provider = provider

    async def extract(self, request: OcrRequest) -> OcrResult:
        return OcrResult(
            request_id=request.document_id,
            provider=self._provider,
            blocks=self._blocks,
            language=request.language,
        )
