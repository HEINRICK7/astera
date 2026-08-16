"""Tests for the Embeddings Plugin boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.embeddings import EmbeddingsPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.embeddings_sdk import DeterministicEmbedder


class EmbeddingsPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_plugin_generates_stable_normalized_batch_vectors(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = EmbeddingsPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicEmbedder(dimensions=4, provider="bge-m3"),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.KNOWLEDGE_EMBEDDINGS,
            {"texts": ["clinical evidence", "patient context"]},
            {},
        )

        self.assertEqual(result["model"], "BAAI/bge-m3")
        self.assertEqual(result["dimensions"], 4)
        self.assertEqual(len(result["vectors"]), 2)
        self.assertEqual(len(result["vectors"][0]["values"]), 4)
        self.assertTrue(capabilities.has_capability(CapabilityType.KNOWLEDGE_EMBEDDINGS))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
