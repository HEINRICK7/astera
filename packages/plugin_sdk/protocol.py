"""Official structural contract implemented by Astera Plugins."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from packages.contracts.plugins import (
    CapabilityType,
    PluginManifest,
    PluginName,
    ProviderName,
)


@runtime_checkable
class PluginProtocol(Protocol):
    """Lifecycle and invocation contract for independently developed plugins."""

    @property
    def plugin_name(self) -> PluginName:
        ...

    @property
    def manifest(self) -> PluginManifest:
        """Versioned metadata advertised by the plugin."""
        ...

    async def on_start(self) -> None:
        """Allocate resources and register capabilities/providers."""
        ...

    async def on_stop(self) -> None:
        """Release resources before the plugin is unloaded."""
        ...

    async def invoke(
        self,
        provider: ProviderName,
        capability: CapabilityType,
        payload: Any,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute one capability request."""
        ...
