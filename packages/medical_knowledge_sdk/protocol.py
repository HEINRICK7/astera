"""Ports used by the Medical Knowledge Layer."""
from __future__ import annotations

from typing import Protocol, Sequence

from .models import (
    Evidence,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSource,
)


class KnowledgeParser(Protocol):
    def parse(
        self,
        *,
        source: KnowledgeSource,
        document_id: str,
        title: str,
        payload: str,
        version: str,
    ) -> KnowledgeDocument:
        """Normalize a source payload into a traceable document."""


class KnowledgeStore(Protocol):
    def upsert(self, document: KnowledgeDocument) -> None:
        """Persist a document revision and make it available for retrieval."""

    def get(self, document_id: str, version: str | None = None) -> KnowledgeDocument | None:
        """Return the current or requested revision."""

    def versions(self, document_id: str) -> tuple[str, ...]:
        """List revisions in insertion order."""

    def search(self, query: KnowledgeQuery) -> Sequence[Evidence]:
        """Return unranked evidence candidates."""


class Ranker(Protocol):
    def rank(self, query: KnowledgeQuery, candidates: Sequence[Evidence]) -> list[Evidence]:
        """Order evidence deterministically for the requested query."""


class KnowledgeRetriever(Protocol):
    def retrieve(self, query: KnowledgeQuery) -> list[Evidence]:
        """Retrieve ranked evidence without exposing storage details."""
