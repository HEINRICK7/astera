"""Tests for the Understanding-to-Knowledge pipeline."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.knowledge import KnowledgePlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.knowledge_pipeline_sdk import SnapshotKnowledgeEngine
from packages.medical_knowledge_sdk import (
    InMemoryKnowledgeStore,
    KeywordRetriever,
    KnowledgeService,
    KnowledgeSource,
    SimpleTextParser,
)


class KnowledgePluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_understanding_snapshot_becomes_versioned_knowledge(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = KnowledgePlugin(
            capabilities,
            providers,
            resolver,
            SnapshotKnowledgeEngine(),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_KNOWLEDGE,
            {
                "encounter_id": "encounter-1",
                "status": "draft",
                "statements": [
                    {
                        "statement_id": "s-1",
                        "text": "Evidence e-1 and e-2 are related.",
                        "evidence_ids": ["e-1", "e-2"],
                        "correlation_ids": ["c-1"],
                        "confidence": 0.8,
                    }
                ],
            },
            {},
        )

        self.assertEqual(result["encounter_id"], "encounter-1")
        self.assertEqual(result["version"], "1")
        self.assertEqual(result["evidence_ids"], ["e-1", "e-2"])
        self.assertEqual(result["correlation_ids"], ["c-1"])
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_KNOWLEDGE))
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_QUERY))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))

    async def test_knowledge_query_is_traceable_to_hypothesis_and_gap(self) -> None:
        store = InMemoryKnowledgeStore()
        service = KnowledgeService(
            parser=SimpleTextParser(),
            store=store,
            retriever=KeywordRetriever(store),
        )
        service.ingest(
            source=KnowledgeSource(
                source_id="guideline-1",
                name="Cardiology guideline",
                kind="guideline",
                version="2026.1",
            ),
            document_id="doc-1",
            title="Acute chest pain",
            payload="ECG and troponin are used in the evaluation of acute chest pain.",
            version="2026.1",
        )
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = KnowledgePlugin(
            capabilities,
            providers,
            resolver,
            SnapshotKnowledgeEngine(),
            retriever=KeywordRetriever(store),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_QUERY,
            {
                "text": "ECG troponin acute chest pain",
                "top_k": 2,
                "hypothesis_id": "hypothesis-acute-coronary-syndrome",
                "gap_id": "gap-ecg",
                "query_type": "missing_fact_evaluation",
            },
            {},
        )

        self.assertEqual(result["query"]["hypothesis_id"], "hypothesis-acute-coronary-syndrome")
        self.assertEqual(result["query"]["gap_id"], "gap-ecg")
        self.assertEqual(result["results"][0]["source_id"], "guideline-1")
        self.assertEqual(result["results"][0]["version"], "2026.1")
        await plugin.on_stop()
