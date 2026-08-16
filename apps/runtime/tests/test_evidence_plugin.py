"""Tests for the Speech-to-Evidence pipeline."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.evidence import EvidencePlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.evidence_sdk import TranscriptEvidenceExtractor


class EvidencePluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_speech_segments_become_traceable_evidence(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = EvidencePlugin(
            capabilities,
            providers,
            resolver,
            TranscriptEvidenceExtractor(),
        )

        await plugin.on_start()
        result = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.COGNITIVE_EVIDENCE,
            {
                "encounter_id": "encounter-1",
                "request_id": "audio-1",
                "provider": "parakeet",
                "language": "pt-BR",
                "segments": [
                    {"text": "Paciente relata dor", "start_ms": 0, "end_ms": 900, "confidence": 0.95},
                ],
            },
            {},
        )

        self.assertEqual(result["encounter_id"], "encounter-1")
        self.assertEqual(result["items"][0]["source_type"], "speech")
        self.assertEqual(result["items"][0]["origin_id"], "audio-1")
        self.assertEqual(result["items"][0]["metadata"]["provider"], "parakeet")
        self.assertTrue(capabilities.has_capability(CapabilityType.COGNITIVE_EVIDENCE))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
