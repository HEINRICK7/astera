from __future__ import annotations

from apps.runtime.src.application.capabilities import CapabilityCatalog, CapabilityRegistry
from apps.runtime.src.domain.entities import CapabilityDescriptor
from apps.runtime.src.domain.value_objects import CapabilityType, PluginName, PluginVersion, ProviderName


def test_capability_catalog_hides_provider_implementation_details() -> None:
    registry = CapabilityRegistry()
    registry.register(
        CapabilityDescriptor(
            capability_type=CapabilityType.SPEECH_TRANSCRIPTION,
            provider=ProviderName("local-speech"),
            plugin=PluginName("speech-plugin"),
            version=PluginVersion(1, 0, 0),
        )
    )

    catalog = CapabilityCatalog(registry)

    assert catalog.list() == [
        {
            "capability": "speech.transcription",
            "providers": ("local-speech",),
            "healthy_providers": 1,
        }
    ]
    assert catalog.contains("speech.transcription")
