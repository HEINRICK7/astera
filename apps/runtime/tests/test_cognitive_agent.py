"""End-to-end test for the first evidence-grounded Cognitive Agent."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.cognitive import CognitiveAgent
from apps.runtime.src.application.plugins.cognitive_agent import CognitiveAgentPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.llm_sdk import DeterministicLlmProvider, ModelRouter
from packages.medical_knowledge_sdk import (
    InMemoryKnowledgeStore,
    KnowledgeQuery,
    KnowledgeService,
    KnowledgeSource,
    KeywordRetriever,
    SimpleTextParser,
)


class CognitiveAgentTests(unittest.IsolatedAsyncioTestCase):
    async def test_evidence_retrieval_to_grounded_response(self) -> None:
        source = KnowledgeSource(
            source_id="guideline-1",
            name="Clinical Guideline",
            kind="official",
            version="2026.1",
        )
        store = InMemoryKnowledgeStore()
        knowledge = KnowledgeService(
            parser=SimpleTextParser(),
            store=store,
            retriever=KeywordRetriever(store),
        )
        knowledge.ingest(
            source=source,
            document_id="document-1",
            title="Glycemic control",
            payload="Glycemic control should be individualized for each patient.",
            version="2026.1",
        )
        agent = CognitiveAgent(
            retriever=KeywordRetriever(store),
            router=ModelRouter(
                {"model": DeterministicLlmProvider("Grounded answer", provider="model")},
                fallback_order=("model",),
            ),
        )
        plugin = CognitiveAgentPlugin(
            CapabilityRegistry(),
            ProviderRegistry(),
            PluginResolver(),
            agent,
        )
        await plugin.on_start()

        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_QUERY,
            {
                "request_id": "query-1",
                "question": "How should glycemic control be individualized?",
            },
            {"session_id": "session-1"},
        )

        self.assertEqual(result["answer"], "Grounded answer")
        self.assertEqual(result["provider"], "model")
        self.assertEqual(result["evidence"][0]["source_id"], "guideline-1")
        self.assertEqual(result["evidence"][0]["version"], "2026.1")

        await plugin.on_stop()
