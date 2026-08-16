"""Clinical Context plugin boundary for context versioning."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.entities.capability_descriptor import CapabilityDescriptor
from apps.runtime.src.domain.entities.provider import Provider
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.domain.value_objects.plugin_name import PluginName
from apps.runtime.src.domain.value_objects.plugin_version import PluginVersion
from apps.runtime.src.domain.value_objects.provider_name import ProviderName
from packages.clinical_context_sdk import ClinicalContext, ClinicalContextBuilder
from packages.clinical_context_sdk.models import parse_datetime
from packages.clinical_facts_sdk import ClinicalFact, ClinicalFactsBatch
from packages.plugin_sdk import PluginManifest


class ClinicalContextPlugin:
    """Expose Clinical Context building through the Astera Plugin SDK."""

    plugin_name = PluginName("clinical-context-plugin")
    provider_name = ProviderName("clinical-context")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral Clinical Context versioning plugin.",
        capabilities=(CapabilityType.COGNITIVE_CLINICAL_CONTEXT,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        builder: ClinicalContextBuilder,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._builder = builder
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.COGNITIVE_CLINICAL_CONTEXT,
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
        if capability != CapabilityType.COGNITIVE_CLINICAL_CONTEXT:
            raise ValueError(f"Unsupported Clinical Context capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("Clinical Context payload must be a dictionary")
        facts = self._facts_batch(payload)
        previous = self._context(payload.get("previous_context"))
        built = await self._builder.build(
            facts=facts,
            previous=previous,
            occurred_at=parse_datetime(payload.get("occurred_at")),
        )
        return built.to_dict()

    @staticmethod
    def _facts_batch(payload: Mapping[str, Any]) -> ClinicalFactsBatch:
        raw = payload.get("facts_batch", payload)
        if not isinstance(raw, Mapping):
            raise TypeError("facts_batch must be a dictionary")
        encounter_id = str(raw["encounter_id"])
        return ClinicalFactsBatch(
            encounter_id=encounter_id,
            items=tuple(ClinicalContextPlugin._fact(item) for item in raw.get("items", ())),
        )

    @staticmethod
    def _fact(item: Mapping[str, Any]) -> ClinicalFact:
        return ClinicalFact(
            fact_id=str(item["id"]),
            category=str(item["category"]),
            value=str(item["value"]),
            unit=str(item["unit"]) if item.get("unit") else None,
            subject_id=str(item["subject"]),
            patient_id=str(item["patient"]) if item.get("patient") else None,
            encounter_id=str(item["encounter"]),
            source=str(item["source"]),
            provenance=item["provenance"],
            confidence=item.get("confidence"),
            certainty=str(item.get("certainty", "reported")),
            polarity=str(item.get("polarity", "positive")),
            observed_at=parse_datetime(item.get("observed_at")),
            valid_at=parse_datetime(item.get("valid_at")),
            status=str(item.get("status", "candidate")),
            metadata=item.get("metadata", {}),
        )

    @staticmethod
    def _context(raw: Any) -> ClinicalContext | None:
        if raw is None:
            return None
        if not isinstance(raw, Mapping):
            raise TypeError("previous_context must be a dictionary")
        facts = tuple(ClinicalContextPlugin._fact(item) for item in raw.get("facts", ()))
        return ClinicalContext(
            context_id=str(raw["context_id"]),
            context_version=int(raw["context_version"]),
            patient_id=str(raw["patient_id"]),
            encounter_id=str(raw["encounter_id"]),
            facts=facts,
            relationships=tuple(raw.get("relationships", ())),
            timeline=tuple(raw.get("timeline", ())),
            hypotheses=tuple(raw.get("hypotheses", ())),
            information_gaps=tuple(raw.get("information_gaps", ())),
            knowledge_references=tuple(raw.get("knowledge_references", ())),
            recommendations=tuple(raw.get("recommendations", ())),
            provenance=raw.get("provenance", {}),
            metadata=raw.get("metadata", {}),
            status=str(raw.get("status", "growing")),
        )
