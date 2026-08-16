"""
Astera Kernel — Inbound Ports (Primary/Driving Ports).

Inbound ports are the interfaces through which external actors
(HTTP, CLI, tests) interact with the Kernel.

The AsteraKernel implements these ports directly.
HTTP adapters depend ONLY on these ports — never on the Kernel class.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from apps.runtime.src.application.orchestrator.task_intent import TaskIntent
from apps.runtime.src.application.orchestrator.task_result import TaskResult
from .evidence import EvidenceIngressPort

__all__ = [
    "CapabilityPort",
    "ContextPort",
    "EvidenceIngressPort",
    "KernelPort",
    "PluginRegistryPort",
    "TaskExecutionPort",
]


class KernelPort(ABC):
    """
    Primary inbound port for Kernel lifecycle and observability.

    Implemented by AsteraKernel.
    Used by: HTTP health adapter, CLI, integration tests.
    """

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Lightweight status (state, ready, version, uptime)."""
        ...

    @abstractmethod
    async def get_health(self) -> dict[str, Any]:
        """Full health report (components, event bus, context, capabilities)."""
        ...

    @abstractmethod
    def get_version_info(self) -> dict[str, Any]:
        """Build and version information (platform, version, build_date)."""
        ...

    @abstractmethod
    def is_ready(self) -> bool:
        """True when the Kernel is operational (READY or DEGRADED)."""
        ...


class CapabilityPort(ABC):
    """
    Inbound port for querying the Capability Registry.

    Used by: API, ADK adapter (Phase D), integration tests.
    """

    @abstractmethod
    async def list_capabilities(self) -> list[dict[str, Any]]:
        """Return all registered capabilities and their status."""
        ...

    @abstractmethod
    async def has_capability(self, capability_type: str) -> bool:
        """True if at least one healthy provider exists for the given type."""
        ...


class ContextPort(ABC):
    """
    Inbound port for Context Manager operations.

    Used by: API session endpoints, ADK (Phase D).
    """

    @abstractmethod
    async def get_active_sessions(self) -> list[dict[str, Any]]:
        """Return a summary of all active sessions."""
        ...


class PluginRegistryPort(ABC):
    """
    Inbound port for Plugin Registry queries.

    Used by: API, Plugin SDK (Phase D).
    """

    @abstractmethod
    async def list_plugins(self) -> list[dict[str, Any]]:
        """Return all registered plugins."""
        ...

    @abstractmethod
    async def get_plugin(self, plugin_name: str) -> dict[str, Any]:
        """Return details of a specific plugin by name."""
        ...


class TaskExecutionPort(ABC):
    """Inbound port for executing a declarative task intent."""

    @abstractmethod
    async def execute_task(self, intent: TaskIntent) -> TaskResult:
        """Execute one capability request through the Kernel."""
        ...
