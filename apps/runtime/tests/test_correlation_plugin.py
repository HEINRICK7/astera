"""Tests for the Evidence-to-Correlation pipeline."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.correlation import CorrelationPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.correlation_sdk import SharedTermCorrelationEngine


class CorrelationPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_related_evidence_produces_explicit_correlation(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = CorrelationPlugin(
            capabilities,
            providers,
            resolver,
            SharedTermCorrelationEngine(),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_CORRELATION,
            {
                "encounter_id": "encounter-1",
                "items": [
                    {"evidence_id": "e-1", "source_type": "speech", "content": "dor torácica", "origin_id": "a-1"},
                    {"evidence_id": "e-2", "source_type": "speech", "content": "dor torácica persistente", "origin_id": "a-1"},
                ],
            },
            {},
        )

        self.assertEqual(result["encounter_id"], "encounter-1")
        self.assertEqual(len(result["correlations"]), 1)
        self.assertEqual(result["correlations"][0]["relation_type"], "shared_term")
        self.assertEqual(result["correlations"][0]["evidence_ids"], ["e-1", "e-2"])
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_CORRELATION))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
