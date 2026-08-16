"""
PluginResolver — maps ProviderName → PluginProtocol instance.

WHY separated from ProviderRegistry:
    ProviderRegistry stores metadata (what providers exist, their status).
    PluginResolver stores live Plugin instances (how to call them).
    Metadata and instances have different lifecycles and concerns.
"""
from __future__ import annotations

import logging

from apps.runtime.src.application.providers.protocol import PluginProtocol
from apps.runtime.src.domain.value_objects.provider_name import ProviderName
from apps.runtime.src.domain.exceptions.provider_not_found import ProviderNotFoundError

logger = logging.getLogger("astera.plugin_resolver")


class PluginResolver:
    """
    Maps ProviderName → PluginProtocol.

    The TaskOrchestrator calls:
        plugin = resolver.resolve(ProviderName("provider-1"))
        result = await plugin.invoke(provider, capability, payload, context)

    Phase D: Plugin SDK populates this when plugins are loaded.
    Phase C: Empty. resolve() raises NotImplementedError with clear guidance.
    """

    def __init__(self) -> None:
        self._registry: dict[ProviderName, PluginProtocol] = {}

    def bind(self, provider: ProviderName, plugin: PluginProtocol) -> None:
        """Bind a Provider name to its Plugin instance."""
        self._registry[provider] = plugin
        logger.info("Provider bound", extra={
            "provider": str(provider),
            "plugin":   str(plugin.plugin_name),
        })

    def unbind(self, provider: ProviderName) -> None:
        """Remove a Provider → Plugin binding."""
        self._registry.pop(provider, None)

    def resolve(self, provider: ProviderName) -> PluginProtocol:
        """
        Resolve a Provider to its Plugin instance.

        Raises:
            NotImplementedError: Phase D not yet loaded.
            ProviderNotFoundError: Provider is registered but has no Plugin bound.
        """
        if not self._registry:
            raise NotImplementedError(
                f"[Phase C] PluginResolver has no bindings. "
                f"The Plugin SDK (Phase D) will populate this. "
                f"Tried to resolve: '{provider}'."
            )
        plugin = self._registry.get(provider)
        if plugin is None:
            raise ProviderNotFoundError(provider)
        return plugin

    def is_bound(self, provider: ProviderName) -> bool:
        return provider in self._registry

    def list_bindings(self) -> dict[str, str]:
        return {str(p): str(pl.plugin_name) for p, pl in self._registry.items()}
