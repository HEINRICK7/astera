"""Reasoning plugin boundary for the Clinical Reasoning Loop."""
from __future__ import annotations

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
from packages.clinical_context_sdk import ClinicalContext
from packages.clinical_context_sdk.models import parse_datetime
from packages.clinical_facts_sdk import ClinicalFact
from packages.plugin_sdk import PluginManifest
from packages.reasoning_sdk import ClinicalReasoner


class ReasoningPlugin:
    """Expose the CRL through the Astera Plugin SDK."""

    plugin_name = PluginName("reasoning-plugin")
    provider_name = ProviderName("reasoning")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral Clinical Reasoning Loop plugin.",
        capabilities=(CapabilityType.COGNITIVE_REASONING,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        reasoner: ClinicalReasoner,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._reasoner = reasoner
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.COGNITIVE_REASONING,
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
        if capability != CapabilityType.COGNITIVE_REASONING:
            raise ValueError(f"Unsupported reasoning capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("reasoning payload must be a dictionary")
        clinical_context = self._context(payload["clinical_context"])
        return (await self._reasoner.reason(clinical_context)).to_dict()

    @staticmethod
    def _context(raw: Any) -> ClinicalContext:
        if not isinstance(raw, Mapping):
            raise TypeError("clinical_context must be a dictionary")
        facts = tuple(ReasoningPlugin._fact(item) for item in raw.get("facts", ()))
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
