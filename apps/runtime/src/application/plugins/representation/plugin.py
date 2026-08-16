"""Representation plugin boundary for SOAP, FHIR, and summary output."""
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
from packages.plugin_sdk import PluginManifest
from packages.representation_sdk import RepresentationEngine, RepresentationRequest


class RepresentationPlugin:
    """Expose knowledge representations through the Plugin SDK."""

    plugin_name = PluginName("representation-plugin")
    provider_name = ProviderName("representation")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Knowledge representation plugin for SOAP, FHIR, and summaries.",
        capabilities=(CapabilityType.COGNITIVE_REPRESENTATION,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        engine: RepresentationEngine,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._engine = engine
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.COGNITIVE_REPRESENTATION,
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
        if capability != CapabilityType.COGNITIVE_REPRESENTATION:
            raise ValueError(f"Unsupported representation capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("representation payload must be a dictionary")
        request = RepresentationRequest(
            record_id=payload["record_id"],
            encounter_id=payload["encounter_id"],
            version=payload["version"],
            statements=tuple(payload["statements"]),
            formats=tuple(payload.get("formats", ("soap", "fhir", "summary"))),
            context_id=payload.get("context_id"),
            context_version=payload.get("context_version"),
            provenance=payload.get("provenance", {}),
            patient_id=payload.get("patient_id"),
            facts=tuple(payload.get("facts", ())),
            transcript=payload.get("transcript"),
            reasoning=payload.get("reasoning"),
        )
        return (await self._engine.render(request)).to_dict()
