"""
Astera Runtime — Inbound Ports (Primary/Driving Ports).

Inbound ports define WHAT the application can do from the outside world's perspective.
They are pure interfaces (ABCs) — no implementation here.

External actors (HTTP, CLI, tests) call the application through these ports.

Rule: Adapters depend on ports. Ports do NOT depend on adapters.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RuntimePort(ABC):
    """
    Inbound port for Runtime lifecycle operations.

    Any adapter that needs to start/stop/inspect the Runtime
    must go through this interface.
    """

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Return the current status of the Runtime."""
        ...

    @abstractmethod
    async def get_health(self) -> dict[str, Any]:
        """Return the health report of all platform components."""
        ...


class PluginRegistryPort(ABC):
    """
    Inbound port for Plugin Registry operations.

    Allows external actors to query the Plugin Registry.
    """

    @abstractmethod
    async def list_plugins(self) -> list[dict[str, Any]]:
        """Return a list of all registered plugins and their status."""
        ...

    @abstractmethod
    async def get_plugin(self, plugin_name: str) -> dict[str, Any]:
        """Return details of a specific plugin by name."""
        ...
