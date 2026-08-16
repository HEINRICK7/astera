"""Embedding plugin boundary for BGE-M3 and compatible providers."""
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
from packages.embeddings_sdk import Embedder, EmbeddingRequest
from packages.plugin_sdk import PluginManifest


class EmbeddingsPlugin:
    """Expose text encoding through the Astera Plugin SDK."""

    plugin_name = PluginName("embeddings-plugin")
    provider_name = ProviderName("embeddings")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral text embeddings plugin.",
        capabilities=(CapabilityType.KNOWLEDGE_EMBEDDINGS,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        embedder: Embedder,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._embedder = embedder
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.KNOWLEDGE_EMBEDDINGS,
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
        if capability != CapabilityType.KNOWLEDGE_EMBEDDINGS:
            raise ValueError(f"Unsupported embeddings capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("embeddings payload must be a dictionary")
        request = EmbeddingRequest(
            texts=tuple(payload["texts"]),
            model=payload.get("model", "BAAI/bge-m3"),
            dimensions=payload.get("dimensions"),
        )
        result = await self._embedder.encode(request)
        return result.to_dict()
