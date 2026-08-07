"""
Astera Kernel — Capability Registry.

The CapabilityRegistry is the central index of everything the platform CAN DO.

Plugin ≠ Capability.

A Plugin registers one or more Capabilities it provides.
The ADK, Agents, and any platform component request a Capability by TYPE —
they never request a Plugin by name.

This decoupling means:
    - Swapping the Speech provider = registering a new Plugin with the same CapabilityType
    - The ADK never changes when implementations change
    - Multiple plugins can provide the same capability (future: routing/load balancing)

Usage in Phase D:
    speech_plugin.register_capability(
        CapabilityType.SPEECH_TRANSCRIPTION,
        version=PluginVersion.from_string("1.0.0"),
    )
    # → CapabilityRegistry now has SPEECH_TRANSCRIPTION available.

    # ADK queries:
    cap = capability_registry.get_best(CapabilityType.SPEECH_TRANSCRIPTION)
    result = await cap.invoke(audio_bytes, context=ctx)
"""
from __future__ import annotations

import logging
from typing import Any

from apps.runtime.src.domain.entities import Capability
from apps.runtime.src.domain.value_objects import (
    CapabilityType,
    HealthStatus,
    PluginName,
    PluginVersion,
)
from apps.runtime.src.domain.exceptions import (
    AsteraError,
    PluginNotFoundError,
)

logger = logging.getLogger("astera.kernel.capabilities")


class CapabilityNotAvailableError(AsteraError):
    def __init__(self, capability_type: CapabilityType) -> None:
        super().__init__(
            f"No healthy plugin registered for capability '{capability_type.value}'.",
            code="CAPABILITY_NOT_AVAILABLE",
        )
        self.capability_type = capability_type


class CapabilityRegistry:
    """
    Central index of all Capabilities available in the Astera platform.

    Indexed by CapabilityType → list[Capability] for fast lookup.
    Maintained separately from the PluginRegistry.

    Lifecycle:
        - Created during Kernel boot (empty)
        - Populated as Plugins register their capabilities (Phase D)
        - Queried by ADK and all Agents (Phase D+)
        - Capability status updated by Health checks
    """

    def __init__(self) -> None:
        # capability_type → list of Capability (sorted by registration order)
        self._index: dict[str, list[Capability]] = {}
        # plugin_name → list of capability IDs it has registered
        self._plugin_capabilities: dict[str, list[str]] = {}

    # ── Registration ──────────────────────────────────────────────────────────

    def register(
        self,
        capability_type: CapabilityType,
        plugin_name: PluginName,
        version: PluginVersion,
        metadata: dict[str, Any] | None = None,
    ) -> Capability:
        """
        Register a Capability offered by a Plugin.

        Called by the Plugin SDK during plugin initialization.
        Not called directly by application code.
        """
        cap = Capability(
            capability_type=capability_type,
            plugin_name=plugin_name,
            version=version,
            status=HealthStatus.UNKNOWN,
            metadata=metadata or {},
        )

        key = capability_type.value
        self._index.setdefault(key, []).append(cap)

        plugin_key = str(plugin_name)
        self._plugin_capabilities.setdefault(plugin_key, []).append(cap.id)

        logger.info(
            "Capability registered",
            extra={
                "capability": capability_type.value,
                "plugin": str(plugin_name),
                "version": str(version),
            },
        )

        return cap

    def unregister_plugin(self, plugin_name: PluginName) -> None:
        """Remove all capabilities offered by a Plugin (called on plugin shutdown)."""
        plugin_key = str(plugin_name)
        capability_ids = self._plugin_capabilities.pop(plugin_key, [])

        for key, caps in self._index.items():
            self._index[key] = [
                c for c in caps if c.id not in capability_ids
            ]

        logger.info(
            "Plugin capabilities unregistered",
            extra={"plugin": plugin_key, "count": len(capability_ids)},
        )

    # ── Query ─────────────────────────────────────────────────────────────────

    def get_best(self, capability_type: CapabilityType) -> Capability:
        """
        Return the best available Capability for a given type.

        'Best' is currently defined as: first HEALTHY registration.
        Future: routing strategies (round-robin, version preference, etc.)

        Raises:
            CapabilityNotAvailableError: if no healthy provider exists.
        """
        caps = self._index.get(capability_type.value, [])
        healthy = [c for c in caps if c.is_available()]

        if not healthy:
            raise CapabilityNotAvailableError(capability_type)

        return healthy[0]

    def list_all(self) -> list[Capability]:
        """Return all registered capabilities (regardless of status)."""
        return [cap for caps in self._index.values() for cap in caps]

    def list_by_type(self, capability_type: CapabilityType) -> list[Capability]:
        """Return all capabilities of a given type."""
        return list(self._index.get(capability_type.value, []))

    def list_by_plugin(self, plugin_name: PluginName) -> list[Capability]:
        """Return all capabilities offered by a specific Plugin."""
        plugin_key = str(plugin_name)
        cap_ids = set(self._plugin_capabilities.get(plugin_key, []))
        return [
            cap
            for caps in self._index.values()
            for cap in caps
            if cap.id in cap_ids
        ]

    def has_capability(self, capability_type: CapabilityType) -> bool:
        """True if at least one healthy provider exists for the given type."""
        return any(c.is_available() for c in self._index.get(capability_type.value, []))

    # ── Health ────────────────────────────────────────────────────────────────

    def mark_healthy(self, capability_id: str) -> None:
        for caps in self._index.values():
            for cap in caps:
                if cap.id == capability_id:
                    cap.mark_healthy()
                    return

    def mark_unhealthy(self, capability_id: str) -> None:
        for caps in self._index.values():
            for cap in caps:
                if cap.id == capability_id:
                    cap.mark_unhealthy()
                    return

    # ── Introspection ─────────────────────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        total = sum(len(v) for v in self._index.values())
        healthy = sum(1 for c in self.list_all() if c.is_available())
        return {
            "total_capabilities": total,
            "healthy_capabilities": healthy,
            "capability_types": list(self._index.keys()),
            "plugins": list(self._plugin_capabilities.keys()),
        }

    def __len__(self) -> int:
        return sum(len(v) for v in self._index.values())

    def __repr__(self) -> str:
        return f"CapabilityRegistry(capabilities={len(self)}, types={len(self._index)})"
