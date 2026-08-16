"""Tests for the Evaluation Plugin boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.evaluation import EvaluationPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.evaluation_sdk import DeterministicEvaluator


class EvaluationPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_plugin_returns_passed_metrics(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = EvaluationPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicEvaluator(provider="deepeval"),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.QUALITY_EVALUATION,
            {
                "request_id": "eval-1",
                "input_text": "What is the status?",
                "output_text": "Stable",
                "reference_text": "Stable",
            },
            {},
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["provider"], "deepeval")
        self.assertEqual(len(result["metrics"]), 2)
        self.assertTrue(capabilities.has_capability(CapabilityType.QUALITY_EVALUATION))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
