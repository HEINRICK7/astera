"""Tests for the Medical NLP Plugin boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.medical_nlp import MedicalNlpPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.medical_nlp_sdk import ClinicalEntity, DeterministicMedicalNlp


class MedicalNlpPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_plugin_registers_and_extracts_entities(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = MedicalNlpPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicMedicalNlp(
                (ClinicalEntity("dor", "SYMPTOM", 0, 3, assertion="present"),),
                provider="medspacy",
            ),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.NLP_ENTITY_EXTRACTION,
            {"request_id": "nlp-1", "text": "dor abdominal", "language": "pt-BR"},
            {"session_id": "session-1"},
        )

        self.assertEqual(result["provider"], "medspacy")
        self.assertEqual(result["entities"][0]["label"], "SYMPTOM")
        self.assertEqual(result["entities"][0]["assertion"], "present")
        self.assertTrue(capabilities.has_capability(CapabilityType.NLP_ENTITY_EXTRACTION))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
