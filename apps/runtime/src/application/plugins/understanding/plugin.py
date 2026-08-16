"""Understanding plugin boundary for provisional cognitive snapshots."""
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
from packages.correlation_sdk import Correlation, CorrelationBatch
from packages.evidence_sdk import EvidenceBatch, EvidenceItem
from packages.plugin_sdk import PluginManifest
from packages.understanding_sdk import UnderstandingEngine


class UnderstandingPlugin:
    """Expose correlation-to-understanding through the Plugin SDK."""

    plugin_name = PluginName("understanding-plugin")
    provider_name = ProviderName("understanding")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provisional evidence-backed understanding plugin.",
        capabilities=(CapabilityType.COGNITIVE_UNDERSTANDING,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        engine: UnderstandingEngine,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._engine = engine
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.COGNITIVE_UNDERSTANDING,
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
        if capability != CapabilityType.COGNITIVE_UNDERSTANDING:
            raise ValueError(f"Unsupported understanding capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("understanding payload must be a dictionary")
        encounter_id = payload["encounter_id"]
        evidence_items = tuple(
            EvidenceItem(
                evidence_id=item["evidence_id"],
                encounter_id=encounter_id,
                source_type=item["source_type"],
                content=item["content"],
                origin_id=item["origin_id"],
                start_ms=item.get("start_ms", 0),
                end_ms=item.get("end_ms", 0),
                confidence=item.get("confidence"),
                speaker=item.get("speaker"),
                metadata=item.get("metadata", {}),
            )
            for item in payload["items"]
        )
        correlations = tuple(
            Correlation(
                correlation_id=item["correlation_id"],
                encounter_id=encounter_id,
                evidence_ids=tuple(item["evidence_ids"]),
                relation_type=item["relation_type"],
                rationale=item["rationale"],
                confidence=item["confidence"],
                metadata=item.get("metadata", {}),
            )
            for item in payload["correlations"]
        )
        snapshot = await self._engine.build(
            evidence=EvidenceBatch(encounter_id=encounter_id, items=evidence_items),
            correlations=CorrelationBatch(encounter_id=encounter_id, correlations=correlations),
        )
        return snapshot.to_dict()
