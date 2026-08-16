"""Tests for the Vision Plugin boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.vision import VisionPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.vision_sdk import DeterministicImageAnalyzer


class VisionPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_plugin_registers_and_analyzes_image(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = VisionPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicImageAnalyzer(
                labels=("document",),
                objects=("page",),
                text="Clinical document",
                provider="vision-benchmark",
            ),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.VISION_CLASSIFICATION,
            {"image_id": "image-1", "image": b"png-bytes"},
            {"session_id": "session-1"},
        )

        self.assertEqual(result["provider"], "vision-benchmark")
        self.assertEqual(result["labels"], ["document"])
        self.assertEqual(result["text"], "Clinical document")
        self.assertTrue(capabilities.has_capability(CapabilityType.VISION_CLASSIFICATION))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
