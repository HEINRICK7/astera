"""OCR plugin boundary for benchmarked document extraction providers."""
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
from packages.ocr_sdk import OcrEngine, OcrRequest
from packages.plugin_sdk import PluginManifest


class OcrPlugin:
    """Expose document text extraction through the Astera Plugin SDK."""

    plugin_name = PluginName("ocr-plugin")
    provider_name = ProviderName("ocr")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral document OCR plugin.",
        capabilities=(CapabilityType.VISION_OCR,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        engine: OcrEngine,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._engine = engine
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.VISION_OCR,
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
        if capability != CapabilityType.VISION_OCR:
            raise ValueError(f"Unsupported OCR capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("OCR payload must be a dictionary")
        request = OcrRequest(
            document_id=str(payload["document_id"]),
            content=payload["content"],
            mime_type=payload.get("mime_type", "application/pdf"),
            language=payload.get("language"),
            metadata={"context": context},
        )
        result = await self._engine.extract(request)
        return result.to_dict()
