"""Application service composing source parsing, storage, and retrieval."""
from __future__ import annotations

from .models import Evidence, KnowledgeQuery, KnowledgeSource
from .protocol import KnowledgeParser, KnowledgeRetriever, KnowledgeStore


class KnowledgeService:
    """Keep Medical Knowledge Layer orchestration independent of providers."""

    def __init__(
        self,
        *,
        parser: KnowledgeParser,
        store: KnowledgeStore,
        retriever: KnowledgeRetriever,
    ) -> None:
        self._parser = parser
        self._store = store
        self._retriever = retriever

    def ingest(
        self,
        *,
        source: KnowledgeSource,
        document_id: str,
        title: str,
        payload: str,
        version: str,
    ) -> None:
        document = self._parser.parse(
            source=source,
            document_id=document_id,
            title=title,
            payload=payload,
            version=version,
        )
        self._store.upsert(document)

    def retrieve(self, query: KnowledgeQuery) -> list[Evidence]:
        return self._retriever.retrieve(query)
