"""Knowledge plugin boundary for consolidated cognitive understanding."""
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
from packages.knowledge_pipeline_sdk import KnowledgeEngine
from packages.medical_knowledge_sdk import KnowledgeQuery, KnowledgeRetriever
from packages.plugin_sdk import PluginManifest
from packages.understanding_sdk import UnderstandingSnapshot, UnderstandingStatement


class KnowledgePlugin:
    """Expose understanding consolidation through the Plugin SDK."""

    plugin_name = PluginName("knowledge-plugin")
    provider_name = ProviderName("knowledge")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Versioned cognitive knowledge consolidation plugin.",
        capabilities=(CapabilityType.COGNITIVE_KNOWLEDGE, CapabilityType.COGNITIVE_QUERY),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        engine: KnowledgeEngine,
        retriever: KnowledgeRetriever | None = None,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._engine = engine
        self._retriever = retriever
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptors = [
            CapabilityDescriptor(
                capability_type=capability,
                provider=self.provider_name,
                plugin=self.plugin_name,
                version=PluginVersion(1, 0, 0),
            )
            for capability in self.manifest.capabilities
        ]
        self._provider = Provider(
            name=self.provider_name,
            plugin=self.plugin_name,
            capabilities=descriptors,
        )
        self._providers.register(self._provider)
        for descriptor in descriptors:
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
        if not isinstance(payload, dict):
            raise TypeError("knowledge payload must be a dictionary")
        if capability == CapabilityType.COGNITIVE_QUERY:
            if self._retriever is None:
                raise RuntimeError("knowledge query capability requires a retriever")
            query = KnowledgeQuery(
                text=str(payload["text"]),
                top_k=int(payload.get("top_k", 5)),
                filters=payload.get("filters", {}),
                hypothesis_id=payload.get("hypothesis_id"),
                gap_id=payload.get("gap_id"),
                query_type=str(payload.get("query_type", "clinical")),
                population=payload.get("population"),
                jurisdiction=payload.get("jurisdiction"),
                as_of=payload.get("as_of"),
            )
            return {
                "query": query.to_dict(),
                "results": [evidence.to_dict() for evidence in self._retriever.retrieve(query)],
            }
        if capability != CapabilityType.COGNITIVE_KNOWLEDGE:
            raise ValueError(f"Unsupported knowledge capability: {capability.value}")
        statements = tuple(
            UnderstandingStatement(
                statement_id=item["statement_id"],
                text=item["text"],
                evidence_ids=tuple(item["evidence_ids"]),
                correlation_ids=tuple(item["correlation_ids"]),
                confidence=item["confidence"],
                metadata=item.get("metadata", {}),
            )
            for item in payload["statements"]
        )
        snapshot = UnderstandingSnapshot(
            encounter_id=payload["encounter_id"],
            statements=statements,
            status=payload.get("status", "draft"),
        )
        return (await self._engine.consolidate(snapshot)).to_dict()
