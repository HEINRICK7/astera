"""Tests for the Clinical Facts-to-Clinical Context boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.clinical_context import ClinicalContextPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.clinical_context_sdk import DeterministicClinicalContextBuilder


def fact(fact_id: str, value: str, *, subject: str = "patient-1") -> dict[str, object]:
    return {
        "id": fact_id,
        "category": "symptom",
        "value": value,
        "subject": subject,
        "patient": subject,
        "encounter": "encounter-1",
        "source": "medical_nlp",
        "provenance": {"source_ref": f"transcript-1:{fact_id}"},
        "certainty": "reported",
        "polarity": "positive",
        "status": "candidate",
    }


class ClinicalContextPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_facts_create_a_versioned_context_and_timeline(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = ClinicalContextPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicClinicalContextBuilder(),
        )

        await plugin.on_start()
        first = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_CLINICAL_CONTEXT,
            {
                "facts_batch": {
                    "encounter_id": "encounter-1",
                    "items": [fact("fact-1", "dor torácica")],
                },
                "occurred_at": "2026-08-07T09:00:00-03:00",
            },
            {},
        )

        self.assertEqual(first["context_version"], 1)
        self.assertEqual(len(first["facts"]), 1)
        self.assertEqual(first["timeline"][0]["event_type"], "clinical.fact.detected")
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_CLINICAL_CONTEXT))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        second = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_CLINICAL_CONTEXT,
            {
                "facts_batch": {
                    "encounter_id": "encounter-1",
                    "items": [fact("fact-2", "dispneia")],
                },
                "previous_context": first,
            },
            {},
        )
        self.assertEqual(second["context_id"], first["context_id"])
        self.assertEqual(second["context_version"], 2)
        self.assertEqual([item["id"] for item in second["facts"]], ["fact-1", "fact-2"])
        self.assertEqual(len(second["timeline"]), 2)

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))

    async def test_context_rejects_a_different_encounter(self) -> None:
        plugin = ClinicalContextPlugin(
            CapabilityRegistry(),
            ProviderRegistry(),
            PluginResolver(),
            DeterministicClinicalContextBuilder(),
        )
        await plugin.on_start()
        with self.assertRaises(ValueError):
            await plugin.invoke(
                plugin.provider_name,
                CapabilityType.COGNITIVE_CLINICAL_CONTEXT,
                {
                    "facts_batch": {
                        "encounter_id": "encounter-2",
                        "items": [fact("fact-2", "febre")],
                    },
                    "previous_context": {
                        "context_id": "context-1",
                        "context_version": 1,
                        "patient_id": "patient-1",
                        "encounter_id": "encounter-1",
                        "facts": [fact("fact-1", "dor")],
                    },
                },
                {},
            )
        await plugin.on_stop()
