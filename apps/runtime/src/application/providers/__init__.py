"""
Astera Kernel — Provider Registry & Plugin Resolver.

THE KEY SEPARATION:
    CapabilityRegistry  → answers "what can the platform do?"
    ProviderRegistry    → answers "who can do it?"
    PluginResolver      → answers "how do I call them?"

The Kernel knows CapabilityRegistry and ProviderRegistry.
The Kernel does NOT directly call Plugins.
The TaskOrchestrator uses PluginResolver to get the actual callable.

Provider lifecycle:
    Plugin starts
        → registers its Providers in ProviderRegistry
        → registers CapabilityDescriptors in CapabilityRegistry
        → Kernel selects providers by capability, not by name
    Plugin stops
        → unregisters from both registries
"""
from __future__ import annotations

import logging
from typing import Any, Protocol, runtime_checkable

from apps.runtime.src.domain.entities import Provider
from apps.runtime.src.domain.value_objects import (
    CapabilityType,
    HealthStatus,
    PluginName,
    ProviderName,
)
from apps.runtime.src.domain.exceptions import ProviderNotFoundError

logger = logging.getLogger("astera.provider_registry")


# ── Plugin Protocol ───────────────────────────────────────────────────────────

@runtime_checkable
class PluginProtocol(Protocol):
    """
    The interface any Astera Plugin MUST implement.

    Defined as a Protocol (structural subtyping) so Plugin SDK can
    wrap any Python class without inheriting from a framework base class.

    Phase D: Plugin SDK implements and enforces this contract.
    Phase C: Only the Protocol definition exists here.
    """

    @property
    def plugin_name(self) -> PluginName:
        """Unique plugin identifier."""
        ...

    async def on_start(self) -> None:
        """Called when the plugin is loaded. Register providers here."""
        ...

    async def on_stop(self) -> None:
        """Called before the plugin is unloaded. Clean up resources."""
        ...

    async def invoke(
        self,
        provider: ProviderName,
        capability: CapabilityType,
        payload: Any,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a capability request.

        Args:
            provider:   Which provider within this plugin should handle it.
            capability: The capability type being invoked.
            payload:    The request data (audio bytes, image, text…).
            context:    The ContextScope as a dict (for LGPD compliance).

        Returns:
            A dict with the result (structure defined by the Provider's contract).
        """
        ...


# ── Plugin Resolver ───────────────────────────────────────────────────────────

class PluginResolver:
    """
    Resolves a Provider name to its Plugin instance.

    The Kernel calls:
        plugin = resolver.resolve(ProviderName("parakeet"))
        result = await plugin.invoke(provider, capability, payload, context)

    Phase D: This is populated by the Plugin SDK when plugins are loaded.
    Phase C: Empty. All resolve() calls raise NotImplementedError with a
             clear message pointing to Phase D.
    """

    def __init__(self) -> None:
        self._registry: dict[ProviderName, PluginProtocol] = {}

    def bind(self, provider: ProviderName, plugin: PluginProtocol) -> None:
        """Bind a Provider name to its Plugin instance."""
        self._registry[provider] = plugin
        logger.info(
            "Provider bound to plugin",
            extra={
                "provider": str(provider),
                "plugin":   str(plugin.plugin_name),
            },
        )

    def unbind(self, provider: ProviderName) -> None:
        """Remove a Provider→Plugin binding."""
        self._registry.pop(provider, None)

    def resolve(self, provider: ProviderName) -> PluginProtocol:
        """
        Resolve a Provider to its Plugin instance.

        Raises:
            ProviderNotFoundError: No plugin bound to this provider.
            NotImplementedError:   Plugin SDK not yet implemented (Phase D stub).
        """
        if not self._registry:
            raise NotImplementedError(
                f"[Phase C] PluginResolver has no bindings yet. "
                f"The Plugin SDK (Phase D) will populate this registry. "
                f"Tried to resolve: '{provider}'."
            )
        plugin = self._registry.get(provider)
        if plugin is None:
            raise ProviderNotFoundError(provider)
        return plugin

    def is_bound(self, provider: ProviderName) -> bool:
        return provider in self._registry

    def list_bindings(self) -> dict[str, str]:
        return {str(p): str(plugin.plugin_name) for p, plugin in self._registry.items()}


# ── Provider Registry ─────────────────────────────────────────────────────────

class ProviderRegistry:
    """
    Registry of all known Providers.

    A Provider is the concrete named entity that implements one or more
    CapabilityDescriptors for a Plugin.

    Data structure:
        _providers[ProviderName] → Provider entity

    Usage:
        # When a plugin starts (Phase D):
        provider_registry.register(Provider(
            name=ProviderName("parakeet"),
            plugin=PluginName("speech-plugin"),
        ))

        # When the Kernel selects a capability:
        provider = provider_registry.get(ProviderName("parakeet"))

        # When a plugin stops:
        provider_registry.unregister_plugin(PluginName("speech-plugin"))
    """

    def __init__(self) -> None:
        self._providers: dict[ProviderName, Provider] = {}

    def register(self, provider: Provider) -> None:
        """Register a Provider. Idempotent (replaces existing by name)."""
        self._providers[provider.name] = provider
        logger.info(
            "Provider registered",
            extra={
                "provider": str(provider.name),
                "plugin":   str(provider.plugin),
            },
        )

    def unregister(self, provider_name: ProviderName) -> None:
        """Remove a Provider by name."""
        removed = self._providers.pop(provider_name, None)
        if removed:
            logger.info("Provider unregistered", extra={"provider": str(provider_name)})

    def unregister_plugin(self, plugin: PluginName) -> int:
        """Remove ALL providers belonging to a plugin. Returns count removed."""
        to_remove = [
            name for name, p in self._providers.items() if p.plugin == plugin
        ]
        for name in to_remove:
            self._providers.pop(name)
        if to_remove:
            logger.info(
                "Plugin providers unregistered",
                extra={"plugin": str(plugin), "removed": len(to_remove)},
            )
        return len(to_remove)

    def get(self, provider_name: ProviderName) -> Provider:
        """
        Retrieve a Provider by name.

        Raises:
            ProviderNotFoundError: Provider not registered.
        """
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
            "total":   len(providers),
            "healthy": sum(1 for p in providers if p.is_active()),
            "providers": [p.to_summary() for p in providers],
        }
