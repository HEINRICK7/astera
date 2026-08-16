"""Echo plugin used to validate the complete Phase C execution chain."""
from __future__ import annotations

from typing import Any

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from packages.plugin_sdk import PluginManifest
from apps.runtime.src.domain.entities.capability_descriptor import CapabilityDescriptor
from apps.runtime.src.domain.entities.provider import Provider
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.domain.value_objects.plugin_name import PluginName
from apps.runtime.src.domain.value_objects.plugin_version import PluginVersion
from apps.runtime.src.domain.value_objects.provider_name import ProviderName


class EchoPlugin:
    """Return the received payload without adding clinical behavior."""

    plugin_name = PluginName("echo-plugin")
    provider_name = ProviderName("echo")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Phase C platform echo capability.",
        capabilities=(CapabilityType.PLATFORM_ECHO,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.PLATFORM_ECHO,
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
        return {
            "provider": str(provider),
            "capability": capability.value,
            "payload": payload,
            "context": context,
        }
