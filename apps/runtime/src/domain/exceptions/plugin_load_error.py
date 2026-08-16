"""PluginLoadError — raised when a Plugin fails to initialize."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError
from apps.runtime.src.domain.value_objects.plugin_name import PluginName


class PluginLoadError(AsteraError):
    """Raised when a plugin's on_start() fails during Kernel bootstrap."""

    def __init__(self, plugin: PluginName, reason: str) -> None:
        super().__init__(
            f"Failed to load plugin '{plugin}': {reason}",
            code="PLUGIN_LOAD_ERROR",
        )
        self.plugin = plugin
