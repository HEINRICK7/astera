"""Terminology plugin boundary for Snowstorm, LOINC, and compatible providers."""
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
from packages.terminology_sdk import TerminologyQuery, TerminologyService


class TerminologyPlugin:
    """Expose terminology lookup through the Astera Plugin SDK."""

    plugin_name = PluginName("terminology-plugin")
    provider_name = ProviderName("terminology")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral medical terminology plugin.",
        capabilities=(CapabilityType.MEDICAL_TERMINOLOGY,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        service: TerminologyService,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._service = service
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.MEDICAL_TERMINOLOGY,
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
        if capability != CapabilityType.MEDICAL_TERMINOLOGY:
            raise ValueError(f"Unsupported terminology capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("terminology payload must be a dictionary")
        query = TerminologyQuery(
            system=payload["system"],
            code=payload.get("code"),
            text=payload.get("text"),
            version=payload.get("version"),
        )
        result = await self._service.lookup(query)
        return result.to_dict()
