"""Evidence plugin boundary for Speech-to-Evidence processing."""
from __future__ import annotations

from typing import Any

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.entities.capability_descriptor import CapabilityDescriptor
from apps.runtime.src.domain.entities.provider import Provider
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.domain.value_objects.plugin_name import PluginName
from apps.runtime.src.domain.value_objects.plugin_version import PluginVersion
from apps.runtime.src.domain.value_objects.provider_name import ProviderName
from packages.evidence_sdk import EvidenceExtractor
from packages.plugin_sdk import PluginManifest
from packages.contracts.transcription import Transcript, TranscriptSegment


class EvidencePlugin:
    """Expose observation-to-evidence conversion through the Plugin SDK."""

    plugin_name = PluginName("evidence-plugin")
    provider_name = ProviderName("evidence")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Speech-to-Evidence clinical pipeline plugin.",
        capabilities=(CapabilityType.COGNITIVE_EVIDENCE,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        extractor: EvidenceExtractor,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._extractor = extractor
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.COGNITIVE_EVIDENCE,
            provider=self.provider_name,
            plugin=self.plugin_name,
            version=PluginVersion(1, 0, 0),
        )
        self._provider = Provider(
            name=self.provider_name,
            plugin=self.plugin_name,
            capabilities=[descriptor],
        )
        self._providers.register(self._provider)
        self._capabilities.register(descriptor)
        self._provider.mark_healthy()
        self._resolver.bind(self.provider_name, self)

    async def on_stop(self) -> None:
        self._resolver.unbind(self.provider_name)
        self._capabilities.unregister_provider(self.provider_name)
        self._providers.unregister(self.provider_name)
        self._provider = None

    async def invoke(
        self,
        provider: ProviderName,
        capability: CapabilityType,
        payload: Any,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if capability != CapabilityType.COGNITIVE_EVIDENCE:
            raise ValueError(f"Unsupported evidence capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("evidence payload must be a dictionary")
        segments = tuple(
            TranscriptSegment(
                segment_id=str(item.get("segment_id", item.get("id", f"segment-{index}"))),
                text=item["text"],
                start_ms=item.get("start_ms", 0),
                end_ms=item.get("end_ms", 0),
                confidence=item.get("confidence"),
                speaker=item.get("speaker"),
            )
            for index, item in enumerate(payload["segments"])
        )
        transcript = Transcript(
            request_id=str(payload["request_id"]),
            language=payload.get("language"),
            provider=payload.get("provider", "speech"),
            segments=segments,
        )
        batch = await self._extractor.extract(
            encounter_id=str(payload["encounter_id"]),
            transcript=transcript,
        )
        return batch.to_dict()
