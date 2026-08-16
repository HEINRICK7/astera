"""Deterministic in-memory adapters for local development and contract tests."""
from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from typing import Sequence

from .models import (
    Evidence,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSource,
)


class SimpleTextParser:
    """Parse plain text into paragraph chunks while preserving source metadata."""

    def parse(
        self,
        *,
        source: KnowledgeSource,
        document_id: str,
        title: str,
        payload: str,
        version: str,
    ) -> KnowledgeDocument:
        if not payload.strip():
            raise ValueError("payload must not be empty")
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", payload) if part.strip()]
        chunks = tuple(
            KnowledgeChunk(
                chunk_id=hashlib.sha256(
                    f"{document_id}:{version}:{position}:{paragraph}".encode()
                ).hexdigest()[:16],
                document_id=document_id,
                text=paragraph,
                position=position,
                metadata={"source_id": source.source_id},
            )
            for position, paragraph in enumerate(paragraphs)
        )
        return KnowledgeDocument(
            document_id=document_id,
            source=source,
            title=title,
            content=payload,
            version=version,
            chunks=chunks,
        )


class InMemoryKnowledgeStore:
    """Revision-aware store used until an approved Knowledge Store adapter exists."""

    def __init__(self) -> None:
        self._revisions: dict[str, list[KnowledgeDocument]] = defaultdict(list)

    def upsert(self, document: KnowledgeDocument) -> None:
        revisions = self._revisions[document.document_id]
        revisions[:] = [item for item in revisions if item.version != document.version]
        revisions.append(document)

    def get(self, document_id: str, version: str | None = None) -> KnowledgeDocument | None:
        revisions = self._revisions.get(document_id, [])
        if version is None:
            return revisions[-1] if revisions else None
        return next((item for item in revisions if item.version == version), None)

    def versions(self, document_id: str) -> tuple[str, ...]:
        return tuple(item.version for item in self._revisions.get(document_id, []))

    def search(self, query: KnowledgeQuery) -> Sequence[Evidence]:
        terms = _terms(query.text)
        candidates: list[Evidence] = []
        for revisions in self._revisions.values():
            document = revisions[-1] if revisions else None
            if document is None or not _matches_filters(document, query):
                continue
            for chunk in document.chunks:
                chunk_terms = _terms(chunk.text)
                matches = len(terms & chunk_terms)
                if matches:
                    candidates.append(
                        Evidence(
                            chunk=chunk,
                            source=document.source,
                            title=document.title,
                            score=matches / len(terms),
                            version=document.version,
                        )
                    )
        return candidates


class KeywordRetriever:
    """Provider-neutral retriever with a replaceable ranking boundary."""

    def __init__(self, store: InMemoryKnowledgeStore) -> None:
        self._store = store

    def retrieve(self, query: KnowledgeQuery) -> list[Evidence]:
        candidates = self._store.search(query)
        return sorted(
            candidates,
            key=lambda item: (-item.score, item.source.source_id, item.chunk.position),
        )[: query.top_k]


def _terms(value: str) -> set[str]:
    return {term.lower() for term in re.findall(r"[\wÀ-ÿ]+", value)}


def _matches_filters(document: KnowledgeDocument, query: KnowledgeQuery) -> bool:
    for key, expected in query.filters.items():
        actual = document.source.metadata.get(key)
        if actual != expected:
            return False
    return True
