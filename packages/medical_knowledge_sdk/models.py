"""Immutable domain contracts for traceable medical knowledge."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _required(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value.strip()


@dataclass(frozen=True, slots=True)
class KnowledgeSource:
    source_id: str
    name: str
    kind: str
    uri: str | None = None
    version: str = "1"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required(self.source_id, "source_id")
        _required(self.name, "name")
        _required(self.kind, "kind")
        _required(self.version, "version")


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    chunk_id: str
    document_id: str
    text: str
    position: int
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required(self.chunk_id, "chunk_id")
        _required(self.document_id, "document_id")
        _required(self.text, "text")
        if self.position < 0:
            raise ValueError("position must be zero or greater")


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    document_id: str
    source: KnowledgeSource
    title: str
    content: str
    version: str
    chunks: tuple[KnowledgeChunk, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required(self.document_id, "document_id")
        _required(self.title, "title")
        _required(self.content, "content")
        _required(self.version, "version")
        for chunk in self.chunks:
            if chunk.document_id != self.document_id:
                raise ValueError("all chunks must belong to the document")


@dataclass(frozen=True, slots=True)
class KnowledgeQuery:
    text: str
    top_k: int = 5
    filters: Mapping[str, Any] = field(default_factory=dict)
    hypothesis_id: str | None = None
    gap_id: str | None = None
    query_type: str = "clinical"
    population: str | None = None
    jurisdiction: str | None = None
    as_of: str | None = None

    def __post_init__(self) -> None:
        _required(self.text, "text")
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        _required(self.query_type, "query_type")

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "top_k": self.top_k,
            "filters": dict(self.filters),
            "hypothesis_id": self.hypothesis_id,
            "gap_id": self.gap_id,
            "query_type": self.query_type,
            "population": self.population,
            "jurisdiction": self.jurisdiction,
            "as_of": self.as_of,
        }


@dataclass(frozen=True, slots=True)
class Evidence:
    chunk: KnowledgeChunk
    source: KnowledgeSource
    title: str
    score: float
    version: str

    def __post_init__(self) -> None:
        _required(self.title, "title")
        _required(self.version, "version")
        if self.score < 0:
            raise ValueError("score must be zero or greater")

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk.chunk_id,
            "document_id": self.chunk.document_id,
            "excerpt": self.chunk.text,
            "source_id": self.source.source_id,
            "source_name": self.source.name,
            "source_kind": self.source.kind,
            "source_uri": self.source.uri,
            "title": self.title,
            "score": self.score,
            "version": self.version,
        }
