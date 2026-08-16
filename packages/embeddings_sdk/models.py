"""Immutable embedding contracts."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmbeddingRequest:
    texts: tuple[str, ...]
    model: str
    dimensions: int | None = None

    def __post_init__(self) -> None:
        if not self.texts or any(not text.strip() for text in self.texts):
            raise ValueError("texts must contain at least one non-empty value")
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if self.dimensions is not None and self.dimensions < 1:
            raise ValueError("dimensions must be positive")


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    index: int
    values: tuple[float, ...]
    model: str

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("index must be zero or greater")
        if not self.values:
            raise ValueError("values must not be empty")
        if not self.model.strip():
            raise ValueError("model must not be empty")


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    model: str
    vectors: tuple[EmbeddingVector, ...]
    dimensions: int

    def to_dict(self) -> dict[str, object]:
        return {
            "model": self.model,
            "dimensions": self.dimensions,
            "vectors": [
                {"index": vector.index, "values": list(vector.values), "model": vector.model}
                for vector in self.vectors
            ],
        }
