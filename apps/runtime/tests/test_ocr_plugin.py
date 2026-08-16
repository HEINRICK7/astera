"""Tests for the OCR Plugin boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.ocr import OcrPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.ocr_sdk import DeterministicOcrEngine, OcrBlock


class OcrPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_plugin_registers_and_extracts_document_text(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = OcrPlugin(
            capabilities,
            providers,
            resolver,
            DeterministicOcrEngine(
                (OcrBlock("Clinical document", page=1, confidence=0.99),),
                provider="ocr-benchmark",
            ),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.VISION_OCR,
            {"document_id": "document-1", "content": b"pdf-bytes", "language": "pt-BR"},
            {"session_id": "session-1"},
        )

        self.assertEqual(result["provider"], "ocr-benchmark")
        self.assertEqual(result["text"], "Clinical document")
        self.assertEqual(result["blocks"][0]["confidence"], 0.99)
        self.assertTrue(capabilities.has_capability(CapabilityType.VISION_OCR))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
