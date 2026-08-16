"""Deterministic local embedder for contract tests."""
from __future__ import annotations

import hashlib
import math

from .models import EmbeddingRequest, EmbeddingResult, EmbeddingVector


class DeterministicEmbedder:
    """Generate stable normalized vectors without model or GPU dependencies."""

    def __init__(self, *, dimensions: int = 8, provider: str = "deterministic") -> None:
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        self._dimensions = dimensions
        self._provider = provider

    async def encode(self, request: EmbeddingRequest) -> EmbeddingResult:
        dimensions = request.dimensions or self._dimensions
        vectors = tuple(
            self._vector(index, text, request.model, dimensions)
            for index, text in enumerate(request.texts)
        )
        return EmbeddingResult(model=request.model, vectors=vectors, dimensions=dimensions)

    def _vector(self, index: int, text: str, model: str, dimensions: int) -> EmbeddingVector:
        values = []
        for position in range(dimensions):
            digest = hashlib.sha256(f"{model}:{text}:{position}".encode()).digest()
            values.append((int.from_bytes(digest[:4], "big") / 2**32) * 2 - 1)
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        normalized = tuple(value / norm for value in values)
        return EmbeddingVector(index=index, values=normalized, model=model)
