"""Clinical Facts plugin boundary for provider-neutral fact candidates."""
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
from packages.clinical_facts_sdk import ClinicalFactsExtractor
from packages.medical_nlp_sdk import ClinicalEntity, NlpResult
from packages.plugin_sdk import PluginManifest


class ClinicalFactsPlugin:
    """Expose Clinical Fact extraction through the Astera Plugin SDK."""

    plugin_name = PluginName("clinical-facts-plugin")
    provider_name = ProviderName("clinical-facts")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral Clinical Facts extraction plugin.",
        capabilities=(CapabilityType.COGNITIVE_CLINICAL_FACTS,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        extractor: ClinicalFactsExtractor,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._extractor = extractor
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.COGNITIVE_CLINICAL_FACTS,
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
        if capability != CapabilityType.COGNITIVE_CLINICAL_FACTS:
            raise ValueError(f"Unsupported Clinical Facts capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("Clinical Facts payload must be a dictionary")

        result = self._nlp_result(payload)
        subject_id = str(payload.get("subject_id") or payload.get("patient_id") or "")
        if not subject_id.strip():
            raise ValueError("Clinical Facts payload requires subject_id or patient_id")
        observed_at = self._parse_datetime(payload.get("observed_at"))
        batch = await self._extractor.extract(
            encounter_id=str(payload["encounter_id"]),
            subject_id=subject_id,
            patient_id=str(payload["patient_id"]) if payload.get("patient_id") else None,
            result=result,
            observed_at=observed_at,
        )
        return batch.to_dict()

    @staticmethod
    def _nlp_result(payload: Mapping[str, Any]) -> NlpResult:
        raw = payload.get("nlp_result", payload)
        if not isinstance(raw, Mapping):
            raise TypeError("nlp_result must be a dictionary")
        entities = tuple(
            ClinicalEntity(
                text=str(item["text"]),
                label=str(item["label"]),
                start=int(item["start"]),
                end=int(item["end"]),
                negated=bool(item.get("negated", False)),
                assertion=str(item.get("assertion", "present")),
            )
            for item in raw.get("entities", ())
        )
        return NlpResult(
            request_id=str(raw["request_id"]),
            provider=str(raw.get("provider", "medical-nlp")),
            language=str(raw.get("language", "pt-BR")),
            entities=entities,
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError("observed_at must be an ISO datetime string")
