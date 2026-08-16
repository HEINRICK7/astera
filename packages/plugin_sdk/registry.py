"""Plugin lifecycle registry for the Astera Plugin SDK."""
from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from packages.plugin_sdk.manifest import PluginManifest
from packages.plugin_sdk.protocol import PluginProtocol

logger = logging.getLogger("astera.plugin_registry")


class PluginLifecycleError(RuntimeError):
    """Raised when a plugin cannot be registered or changes lifecycle state."""


@dataclass
class PluginRecord:
    """Runtime metadata for one registered plugin instance."""

    plugin: PluginProtocol
    manifest: PluginManifest
    state: str = "registered"
    started_at: datetime | None = None
    error: str | None = None

    def summary(self) -> dict[str, Any]:
        return {
            "plugin": str(self.plugin.plugin_name),
            "manifest": self.manifest.to_summary(),
            "state": self.state,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "error": self.error,
        }


class PluginRegistry:
    """Own plugin instances and execute lifecycle transitions in order."""

    def __init__(self) -> None:
        self._records: dict[str, PluginRecord] = {}

    def register(self, plugin: PluginProtocol) -> None:
        name = str(plugin.plugin_name)
        if name in self._records:
            raise PluginLifecycleError(f"Plugin '{name}' is already registered.")
        if plugin.manifest.name != plugin.plugin_name:
            raise PluginLifecycleError(
                f"Plugin manifest name does not match '{name}'."
            )
        self._records[name] = PluginRecord(plugin=plugin, manifest=plugin.manifest)
        logger.info("Plugin registered", extra={"plugin": name})

    def discover(self, plugins: Iterable[PluginProtocol]) -> list[str]:
        """Register discovered plugin instances and return their names."""
        discovered: list[str] = []
        for plugin in plugins:
            self.register(plugin)
            discovered.append(str(plugin.plugin_name))
        return discovered

    def get(self, plugin_name: str) -> PluginProtocol:
        try:
            return self._records[plugin_name].plugin
        except KeyError as exc:
            raise PluginLifecycleError(f"Plugin '{plugin_name}' is not registered.") from exc

    async def start(self, plugin_name: str) -> None:
        record = self._record(plugin_name)
        if record.state == "started":
            return
        try:
            await record.plugin.on_start()
        except Exception as exc:
            record.state = "failed"
            record.error = str(exc)
            raise PluginLifecycleError(
                f"Plugin '{plugin_name}' failed to start: {exc}"
            ) from exc
        record.state = "started"
        record.started_at = datetime.now(tz=timezone.utc)

    async def stop(self, plugin_name: str) -> None:
        record = self._record(plugin_name)
        if record.state != "started":
            return
        try:
            await record.plugin.on_stop()
        except Exception as exc:
            record.state = "failed"
            record.error = str(exc)
            raise PluginLifecycleError(
                f"Plugin '{plugin_name}' failed to stop: {exc}"
            ) from exc
        record.state = "stopped"

    async def start_all(self) -> None:
        for name in self._records:
            await self.start(name)

    async def stop_all(self) -> None:
        for name in reversed(tuple(self._records)):
            await self.stop(name)

    def list_all(self) -> list[dict[str, Any]]:
        return [record.summary() for record in self._records.values()]

    def summary(self) -> dict[str, Any]:
        records = self.list_all()
        return {
            "total": len(records),
            "started": sum(record["state"] == "started" for record in records),
            "plugins": records,
        }

    def health(self) -> list[dict[str, Any]]:
        """Return the health view consumed by platform health reporting."""
        return [
            {
                "plugin": record["plugin"],
                "healthy": record["state"] == "started",
                "state": record["state"],
                "error": record["error"],
            }
            for record in self.list_all()
        ]

    def get_summary(self, plugin_name: str) -> dict[str, Any]:
        """Return one plugin summary for the public API."""
        for record in self.list_all():
            if record["plugin"] == plugin_name:
                return record
        raise PluginLifecycleError(f"Plugin '{plugin_name}' is not registered.")

    def _record(self, plugin_name: str) -> PluginRecord:
        try:
            return self._records[plugin_name]
        except KeyError as exc:
            raise PluginLifecycleError(f"Plugin '{plugin_name}' is not registered.") from exc
