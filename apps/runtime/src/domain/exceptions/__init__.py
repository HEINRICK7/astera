"""
Astera Kernel — Domain Exception Hierarchy.

All Astera exceptions inherit from AsteraError.
HTTP adapters catch these and map them to appropriate status codes.
"""
from __future__ import annotations

from apps.runtime.src.domain.value_objects import (
    CapabilityType,
    PluginName,
    ProviderName,
)


# ── Root ──────────────────────────────────────────────────────────────────────

class AsteraError(Exception):
    """Root exception for all Astera platform errors."""

    def __init__(self, message: str, code: str = "ASTERA_ERROR") -> None:
        super().__init__(message)
        self.code = code

    @property
    def message(self) -> str:
        return str(self)


# ── Kernel / Runtime ──────────────────────────────────────────────────────────

class RuntimeNotReadyError(AsteraError):
    def __init__(self) -> None:
        super().__init__(
            "The Kernel is not ready to serve requests.",
            code="KERNEL_NOT_READY",
        )


class EventBusError(AsteraError):
    def __init__(self, detail: str) -> None:
        super().__init__(f"Event Bus error: {detail}", code="EVENT_BUS_ERROR")


# ── Capability ────────────────────────────────────────────────────────────────

class CapabilityNotFoundError(AsteraError):
    def __init__(self, capability_type: CapabilityType) -> None:
        super().__init__(
            f"No provider registered for capability '{capability_type.value}'.",
            code="CAPABILITY_NOT_FOUND",
        )
        self.capability_type = capability_type


class NoHealthyProviderError(AsteraError):
    def __init__(
        self,
        capability_type: CapabilityType,
        criteria=None,
    ) -> None:
        detail = f"No healthy provider found for capability '{capability_type.value}'"
        if criteria and not criteria.is_empty():
            detail += f" with the requested criteria."
        super().__init__(detail, code="NO_HEALTHY_PROVIDER")
        self.capability_type = capability_type
        self.criteria = criteria


# ── Provider ──────────────────────────────────────────────────────────────────

class ProviderNotFoundError(AsteraError):
    def __init__(self, provider: ProviderName) -> None:
        super().__init__(
            f"Provider '{provider}' is not registered in the ProviderRegistry.",
            code="PROVIDER_NOT_FOUND",
        )
        self.provider = provider


# ── Plugin ────────────────────────────────────────────────────────────────────

class PluginNotFoundError(AsteraError):
    def __init__(self, plugin: PluginName) -> None:
        super().__init__(
            f"Plugin '{plugin}' is not registered.",
            code="PLUGIN_NOT_FOUND",
        )
        self.plugin = plugin


class PluginLoadError(AsteraError):
    def __init__(self, plugin: PluginName, reason: str) -> None:
        super().__init__(
            f"Failed to load plugin '{plugin}': {reason}",
            code="PLUGIN_LOAD_ERROR",
        )
        self.plugin = plugin


# ── Orchestration ─────────────────────────────────────────────────────────────

class TaskExecutionError(AsteraError):
    def __init__(self, request_id: str, reason: str) -> None:
        super().__init__(
            f"Task '{request_id}' failed: {reason}",
            code="TASK_EXECUTION_ERROR",
        )
        self.request_id = request_id


# ── Context ───────────────────────────────────────────────────────────────────

class ContextNotFoundError(AsteraError):
    def __init__(self, context_id: str) -> None:
        super().__init__(
            f"Context '{context_id}' not found.",
            code="CONTEXT_NOT_FOUND",
        )
        self.context_id = context_id
