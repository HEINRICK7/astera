"""Tests for the Correlation-to-Understanding pipeline."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.understanding import UnderstandingPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.understanding_sdk import CorrelationUnderstandingEngine


class UnderstandingPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_correlation_becomes_reviewable_understanding(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = UnderstandingPlugin(
            capabilities,
            providers,
            resolver,
            CorrelationUnderstandingEngine(),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_UNDERSTANDING,
            {
                "encounter_id": "encounter-1",
                "items": [
                    {"evidence_id": "e-1", "source_type": "speech", "content": "dor", "origin_id": "a-1"},
                    {"evidence_id": "e-2", "source_type": "speech", "content": "dor persistente", "origin_id": "a-1"},
                ],
                "correlations": [
                    {
                        "correlation_id": "c-1",
                        "evidence_ids": ["e-1", "e-2"],
                        "relation_type": "shared_term",
                        "rationale": "Shared terms: dor",
                        "confidence": 0.8,
                    }
                ],
            },
            {},
        )

        self.assertEqual(result["encounter_id"], "encounter-1")
        self.assertEqual(result["status"], "draft")
        self.assertIn("e-1, e-2", result["statements"][0]["text"])
        self.assertEqual(result["statements"][0]["correlation_ids"], ["c-1"])
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_UNDERSTANDING))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
