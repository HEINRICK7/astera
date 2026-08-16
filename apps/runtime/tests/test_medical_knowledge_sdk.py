"""Contract tests for the Medical Knowledge Layer foundation."""
from __future__ import annotations

import unittest

from packages.medical_knowledge_sdk import (
    InMemoryKnowledgeStore,
    KnowledgeQuery,
    KnowledgeService,
    KnowledgeSource,
    KeywordRetriever,
    SimpleTextParser,
)


class MedicalKnowledgeSdkTests(unittest.TestCase):
    def test_ingest_retrieve_and_source_filter_are_traceable(self) -> None:
        source = KnowledgeSource(
            source_id="pcdt-diabetes",
            name="PCDT Diabetes",
            kind="official_brazilian",
            uri="https://example.invalid/pcdt",
            version="2026.1",
            metadata={"jurisdiction": "BR"},
        )
        store = InMemoryKnowledgeStore()
        service = KnowledgeService(
            parser=SimpleTextParser(),
            store=store,
            retriever=KeywordRetriever(store),
        )
        service.ingest(
            source=source,
            document_id="guideline-1",
            title="Diabetes guideline",
            payload="Glycemic control should be individualized.\n\nFollow-up includes laboratory monitoring.",
            version="2026.1",
        )

        evidence = service.retrieve(
            KnowledgeQuery("glycemic control", filters={"jurisdiction": "BR"})
        )

        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0].source.source_id, "pcdt-diabetes")
        self.assertEqual(evidence[0].version, "2026.1")
        self.assertEqual(store.versions("guideline-1"), ("2026.1",))

    def test_store_keeps_revisions_and_retriever_uses_latest(self) -> None:
        source = KnowledgeSource(source_id="source-1", name="Source", kind="guideline")
        store = InMemoryKnowledgeStore()
        service = KnowledgeService(
            parser=SimpleTextParser(),
            store=store,
            retriever=KeywordRetriever(store),
        )
        for version, text in (("1", "Initial recommendation."), ("2", "Updated recommendation.")):
            service.ingest(
                source=source,
                document_id="document-1",
                title="Recommendation",
                payload=text,
                version=version,
            )

        self.assertEqual(store.versions("document-1"), ("1", "2"))
        evidence = service.retrieve(KnowledgeQuery("updated"))
        self.assertEqual(evidence[0].version, "2")
        self.assertEqual(store.get("document-1", version="1").version, "1")
