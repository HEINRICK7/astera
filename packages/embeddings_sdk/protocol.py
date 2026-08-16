"""Embedding provider port."""
from __future__ import annotations

from typing import Protocol

from .models import EmbeddingRequest, EmbeddingResult


class Embedder(Protocol):
    async def encode(self, request: EmbeddingRequest) -> EmbeddingResult:
        """Encode text without exposing model-specific APIs."""
