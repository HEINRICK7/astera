"""Tests for the Terminology Plugin boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.terminology import TerminologyPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.terminology_sdk import (
    DeterministicTerminologyService,
    TerminologyConcept,
)


class TerminologyPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_plugin_looks_up_versioned_concept(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = TerminologyPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicTerminologyService(
                (
                    TerminologyConcept(
                        system="http://loinc.org",
                        code="4548-4",
                        display="Hemoglobin A1c",
                        version="2.78",
                    ),
                ),
                provider="loinc",
            ),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.MEDICAL_TERMINOLOGY,
            {"system": "http://loinc.org", "code": "4548-4", "version": "2.78"},
            {"session_id": "session-1"},
        )

        self.assertEqual(result["provider"], "loinc")
        self.assertEqual(result["concepts"][0]["display"], "Hemoglobin A1c")
        self.assertEqual(result["concepts"][0]["version"], "2.78")
        self.assertTrue(capabilities.has_capability(CapabilityType.MEDICAL_TERMINOLOGY))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
