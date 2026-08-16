"""Tests for the Clinical Reasoning Loop boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.reasoning import ReasoningPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.clinical_context_sdk import ClinicalContext
from packages.clinical_facts_sdk import ClinicalFact
from packages.reasoning_sdk import DeterministicClinicalReasoner


def make_context() -> ClinicalContext:
    facts = tuple(
        ClinicalFact(
            fact_id=f"fact-{index}",
            category=category,
            value=value,
            subject_id="patient-1",
            patient_id="patient-1",
            encounter_id="encounter-1",
            source="medical_nlp",
            provenance={"source_ref": f"transcript-1:{index}"},
        )
        for index, (category, value) in enumerate((
            ("symptom", "dor no peito"),
            ("symptom", "falta de ar"),
            ("condition", "hipertensão"),
        ))
    )
    return ClinicalContext(
        context_id="context-1",
        context_version=1,
        patient_id="patient-1",
        encounter_id="encounter-1",
        facts=facts,
    )


class ReasoningPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_context_generates_competing_hypotheses_and_questions(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = ReasoningPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicClinicalReasoner(),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_REASONING,
            {"clinical_context": make_context().to_dict()},
            {},
        )

        self.assertEqual(result["encounter_id"], "encounter-1")
        self.assertEqual(len(result["hypotheses"]), 3)
        self.assertEqual(result["hypotheses"][0]["status"], "candidate")
        self.assertIn("fact-0", result["hypotheses"][0]["supporting_facts"])
        self.assertTrue(result["information_gaps"])
        self.assertEqual(
            {gap["missing_fact_type"] for gap in result["information_gaps"]},
            {"ECG", "troponina"},
        )
        self.assertEqual(
            {question["gap_id"] for question in result["questions"]},
            {gap["id"] for gap in result["information_gaps"]},
        )
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_REASONING))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))

    async def test_reasoning_rejects_an_invalid_context_payload(self) -> None:
        plugin = ReasoningPlugin(
            CapabilityRegistry(),
            ProviderRegistry(),
            PluginResolver(),
            DeterministicClinicalReasoner(),
        )
        await plugin.on_start()
        with self.assertRaises((KeyError, TypeError, ValueError)):
            await plugin.invoke(
                plugin.provider_name,
                CapabilityType.COGNITIVE_REASONING,
                {"clinical_context": {"context_id": "missing-fields"}},
                {},
            )
        await plugin.on_stop()
