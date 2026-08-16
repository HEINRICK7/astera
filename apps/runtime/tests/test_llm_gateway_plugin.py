"""Tests for the LiteLLM-compatible gateway boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.llm_gateway import LlmGatewayPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.llm_sdk import DeterministicLlmProvider, ModelRouter


class FailingProvider:
    async def complete(self, request):
        raise RuntimeError("upstream unavailable")


class LlmGatewayPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_gateway_selects_fallback_provider(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        router = ModelRouter(
            {"primary": FailingProvider(), "fallback": DeterministicLlmProvider("Fallback response", provider="fallback")},
            fallback_order=("primary", "fallback"),
        )
        plugin = LlmGatewayPlugin(capabilities, providers, resolver, router)

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.AI_TEXT_GENERATION,
            {"messages": [{"role": "user", "content": "Hello"}], "model": "gemini-2.0-flash"},
            {},
        )

        self.assertEqual(result["provider"], "fallback")
        self.assertEqual(result["content"], "Fallback response")
        self.assertTrue(capabilities.has_capability(CapabilityType.AI_TEXT_GENERATION))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
