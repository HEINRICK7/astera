"""Medical NLP plugin boundary for entity and assertion providers."""
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
from packages.medical_nlp_sdk import MedicalNlpProcessor, NlpRequest
from packages.plugin_sdk import PluginManifest


class MedicalNlpPlugin:
    """Expose medical text extraction through the Astera Plugin SDK."""

    plugin_name = PluginName("medical-nlp-plugin")
    provider_name = ProviderName("medical-nlp")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral clinical text processing plugin.",
        capabilities=(CapabilityType.NLP_ENTITY_EXTRACTION,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        processor: MedicalNlpProcessor,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._processor = processor
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.NLP_ENTITY_EXTRACTION,
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
        if capability != CapabilityType.NLP_ENTITY_EXTRACTION:
            raise ValueError(f"Unsupported Medical NLP capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("Medical NLP payload must be a dictionary")
        request = NlpRequest(
            request_id=str(payload["request_id"]),
            text=payload["text"],
            language=payload.get("language", "pt-BR"),
            metadata={"context": context},
        )
        result = await self._processor.process(request)
        return result.to_dict()
