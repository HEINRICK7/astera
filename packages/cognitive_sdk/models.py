"""Immutable cognitive query and response contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CognitiveRequest:
    request_id: str
    question: str
    top_k: int = 3
    model: str = "default"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_id.strip() or not self.question.strip():
            raise ValueError("request_id and question must not be empty")
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        if not self.model.strip():
            raise ValueError("model must not be empty")


@dataclass(frozen=True, slots=True)
class CognitiveEvidence:
    source_id: str
    document_id: str
    chunk_id: str
    title: str
    excerpt: str
    score: float
    version: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "title": self.title,
            "excerpt": self.excerpt,
            "score": self.score,
            "version": self.version,
        }


@dataclass(frozen=True, slots=True)
class CognitiveResponse:
    request_id: str
    answer: str
    provider: str
    model: str
    evidence: tuple[CognitiveEvidence, ...]

    def __post_init__(self) -> None:
        if not self.request_id.strip() or not self.answer.strip():
            raise ValueError("request_id and answer must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "answer": self.answer,
            "provider": self.provider,
            "model": self.model,
            "evidence": [evidence.to_dict() for evidence in self.evidence],
        }
