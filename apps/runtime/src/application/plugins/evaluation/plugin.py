"""Evaluation plugin boundary for DeepEval and compatible providers."""
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
from packages.evaluation_sdk import EvaluationRequest, Evaluator
from packages.plugin_sdk import PluginManifest


class EvaluationPlugin:
    """Expose quality metrics through the Astera Plugin SDK."""

    plugin_name = PluginName("evaluation-plugin")
    provider_name = ProviderName("evaluation")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral AI response evaluation plugin.",
        capabilities=(CapabilityType.QUALITY_EVALUATION,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        evaluator: Evaluator,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._evaluator = evaluator
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.QUALITY_EVALUATION,
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
        if capability != CapabilityType.QUALITY_EVALUATION:
            raise ValueError(f"Unsupported evaluation capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("evaluation payload must be a dictionary")
        request = EvaluationRequest(
            request_id=str(payload["request_id"]),
            input_text=payload["input_text"],
            output_text=payload["output_text"],
            reference_text=payload.get("reference_text"),
            metadata={"context": context},
        )
        result = await self._evaluator.evaluate(request)
        return result.to_dict()
