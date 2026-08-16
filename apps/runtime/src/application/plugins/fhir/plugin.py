"""FHIR plugin boundary for HAPI FHIR and compatible gateways."""
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
from packages.fhir_sdk import FhirGateway, FhirResource
from packages.plugin_sdk import PluginManifest


class FhirPlugin:
    """Expose FHIR mapping and interoperability through the Plugin SDK."""

    plugin_name = PluginName("fhir-plugin")
    provider_name = ProviderName("fhir")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="Provider-neutral HL7 FHIR interoperability plugin.",
        capabilities=(CapabilityType.MEDICAL_FHIR,),
    )

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        gateway: FhirGateway,
    ) -> None:
        self._capabilities = capabilities
        self._providers = providers
        self._resolver = resolver
        self._gateway = gateway
        self._provider: Provider | None = None

    async def on_start(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_type=CapabilityType.MEDICAL_FHIR,
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
        if capability != CapabilityType.MEDICAL_FHIR:
            raise ValueError(f"Unsupported FHIR capability: {capability.value}")
        if not isinstance(payload, dict):
            raise TypeError("FHIR payload must be a dictionary")
        operation = payload.get("operation", "validate")
        if operation == "validate":
            resource = FhirResource.from_dict(payload["resource"])
            errors = await self._gateway.validate(resource)
            return {"valid": not errors, "errors": list(errors), "resource": resource.to_dict()}
        if operation == "create":
            resource = FhirResource.from_dict(payload["resource"])
            created = await self._gateway.create(resource)
            return {"resource": created.to_dict()}
        if operation == "read":
            resource = await self._gateway.read(payload["resource_type"], payload["resource_id"])
            return {"resource": resource.to_dict() if resource else None}
        if operation == "bundle":
            resources = tuple(FhirResource.from_dict(item) for item in payload["resources"])
            bundle = await self._gateway.bundle(resources, payload.get("bundle_type", "collection"))
            return {"bundle": bundle.to_dict()}
        raise ValueError(f"Unsupported FHIR operation: {operation}")
