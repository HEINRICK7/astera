"""Tests for the Medical NLP-to-Clinical Facts boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.clinical_facts import ClinicalFactsPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.clinical_facts_sdk import DeterministicClinicalFactsExtractor


class ClinicalFactsPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_nlp_entities_become_traceable_clinical_facts(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = ClinicalFactsPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicClinicalFactsExtractor(),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_CLINICAL_FACTS,
            {
                "encounter_id": "encounter-1",
                "patient_id": "patient-1",
                "nlp_result": {
                    "request_id": "transcript-1",
                    "provider": "medical-nlp",
                    "language": "pt-BR",
                    "entities": [
                        {
                            "text": "dor torácica",
                            "label": "symptom",
                            "start": 0,
                            "end": 12,
                        },
                    ],
                },
            },
            {},
        )

        fact = result["items"][0]
        self.assertEqual(result["encounter_id"], "encounter-1")
        self.assertEqual(fact["category"], "symptom")
        self.assertEqual(fact["value"], "dor torácica")
        self.assertEqual(fact["patient"], "patient-1")
        self.assertEqual(fact["source"], "medical_nlp")
        self.assertEqual(fact["polarity"], "positive")
        self.assertEqual(fact["status"], "candidate")
        self.assertEqual(fact["provenance"]["source_ref"], "transcript-1:0-12")
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_CLINICAL_FACTS))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))

    async def test_negated_and_uncertain_assertions_remain_explicit(self) -> None:
        plugin = ClinicalFactsPlugin(
            CapabilityRegistry(),
            ProviderRegistry(),
            PluginResolver(),
            DeterministicClinicalFactsExtractor(),
        )
        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_CLINICAL_FACTS,
            {
                "encounter_id": "encounter-2",
                "subject_id": "patient-2",
                "nlp_result": {
                    "request_id": "transcript-2",
                    "entities": [
                        {"text": "febre", "label": "symptom", "start": 0, "end": 5, "negated": True},
                        {"text": "pneumonia", "label": "condition", "start": 6, "end": 15, "assertion": "possible"},
                    ],
                },
            },
            {},
        )

        self.assertEqual(result["items"][0]["polarity"], "negative")
        self.assertEqual(result["items"][0]["certainty"], "reported")
        self.assertEqual(result["items"][1]["polarity"], "positive")
        self.assertEqual(result["items"][1]["certainty"], "uncertain")
        await plugin.on_stop()

    async def test_invalid_subject_is_rejected(self) -> None:
        plugin = ClinicalFactsPlugin(
            CapabilityRegistry(),
            ProviderRegistry(),
            PluginResolver(),
            DeterministicClinicalFactsExtractor(),
        )
        await plugin.on_start()
        with self.assertRaises(ValueError):
            await plugin.invoke(
                plugin.provider_name,
                CapabilityType.COGNITIVE_CLINICAL_FACTS,
                {
                    "encounter_id": "encounter-3",
                    "nlp_result": {"request_id": "transcript-3", "entities": []},
                },
                {},
            )
        await plugin.on_stop()
