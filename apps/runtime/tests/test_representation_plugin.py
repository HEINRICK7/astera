"""Tests for the Knowledge-to-Representation pipeline."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.representation import RepresentationPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.representation_sdk import KnowledgeRepresentationEngine


class RepresentationPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_knowledge_renders_to_soap_fhir_and_summary(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = RepresentationPlugin(
            capabilities,
            providers,
            resolver,
            KnowledgeRepresentationEngine(),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_REPRESENTATION,
            {
                "record_id": "record-1",
                "encounter_id": "encounter-1",
                "version": "1",
                "statements": ["Evidence e-1 and e-2 are related."],
                "context_id": "context-1",
                "context_version": 3,
                "provenance": {"source": "clinical-context"},
            },
            {},
        )

        formats = {item["format"]: item for item in result["representations"]}
        self.assertEqual(set(formats), {"soap", "fhir", "summary"})
        self.assertEqual(formats["soap"]["content"]["status"], "draft")
        self.assertEqual(formats["fhir"]["content"]["resourceType"], "DocumentReference")
        self.assertIn("e-1", formats["summary"]["content"])
        self.assertEqual(formats["soap"]["context_id"], "context-1")
        self.assertEqual(formats["fhir"]["context_version"], 3)
        self.assertEqual(formats["summary"]["provenance"]["source"], "clinical-context")
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_REPRESENTATION))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
