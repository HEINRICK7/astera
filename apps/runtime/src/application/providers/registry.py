"""
ProviderRegistry — index of all known Providers.

WHY separated from CapabilityRegistry:
    CapabilityRegistry answers: "What can the platform do?"
    ProviderRegistry answers:   "Who can do it, and are they healthy?"
    Separation allows health-checking providers independently of capabilities.
"""
from __future__ import annotations

import logging
from typing import Any

from apps.runtime.src.domain.entities.provider import Provider
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.domain.value_objects.plugin_name import PluginName
from apps.runtime.src.domain.value_objects.provider_name import ProviderName
from apps.runtime.src.domain.exceptions.provider_not_found import ProviderNotFoundError

logger = logging.getLogger("astera.provider_registry")


class ProviderRegistry:
    """
    Index: ProviderName → Provider entity.

    A Provider is a named implementation that fulfils one or more capabilities.
    It belongs to exactly ONE Plugin. One Plugin can host multiple Providers.
    """

    def __init__(self) -> None:
        self._providers: dict[ProviderName, Provider] = {}

    def register(self, provider: Provider) -> None:
        """Register a Provider. Idempotent by name."""
        self._providers[provider.name] = provider
        logger.info("Provider registered", extra={
            "provider": str(provider.name),
            "plugin":   str(provider.plugin),
        })

    def unregister(self, provider_name: ProviderName) -> None:
        removed = self._providers.pop(provider_name, None)
        if removed:
            logger.info("Provider unregistered", extra={"provider": str(provider_name)})

    def unregister_plugin(self, plugin: PluginName) -> int:
        """Remove all providers belonging to a plugin. Returns count removed."""
        to_remove = [n for n, p in self._providers.items() if p.plugin == plugin]
        for name in to_remove:
            self._providers.pop(name)
        return len(to_remove)

    def get(self, provider_name: ProviderName) -> Provider:
        """Raises ProviderNotFoundError if not registered."""
        provider = self._providers.get(provider_name)
        if provider is None:
            raise ProviderNotFoundError(provider_name)
        return provider

    def list_all(self) -> list[Provider]:
        return list(self._providers.values())

    def list_for_capability(self, capability_type: CapabilityType) -> list[Provider]:
        return [p for p in self._providers.values() if p.supports_capability(capability_type)]

    def mark_healthy(self, provider_name: ProviderName) -> None:
        if provider_name in self._providers:
            self._providers[provider_name].mark_healthy()

    def mark_unhealthy(self, provider_name: ProviderName) -> None:
        if provider_name in self._providers:
            self._providers[provider_name].mark_unhealthy()

    def summary(self) -> dict[str, Any]:
        providers = self.list_all()
        return {
            "total":     len(providers),
            "healthy":   sum(1 for p in providers if p.is_active()),
            "providers": [p.to_summary() for p in providers],
        }
