"""PluginNotFoundError — raised when a Plugin is not registered."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError
from apps.runtime.src.domain.value_objects.plugin_name import PluginName


class PluginNotFoundError(AsteraError):
    """Raised when the PluginResolver cannot find a binding for the given PluginName."""

    def __init__(self, plugin: PluginName) -> None:
        super().__init__(
            f"Plugin '{plugin}' is not registered.",
            code="PLUGIN_NOT_FOUND",
        )
        self.plugin = plugin
