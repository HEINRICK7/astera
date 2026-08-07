"""
Astera Kernel — The Platform Operating System.

The AsteraKernel is NOT a server. It is NOT a service.
It is the operating system of the Astera platform.

Every capability (Speech, Vision, OCR, Medical NLP, Google ADK, etc.)
exists only as an extension registered in this Kernel.

Bootstrap sequence:
    BOOTING
        → configure logging
        → load configuration
        → connect Event Bus
        → initialize Context Manager
        → initialize Plugin Registry
        → initialize Capability Registry
        → initialize Health Manager
        → start Lifecycle Manager
    READY
        → API starts accepting requests
        → Plugins can register capabilities
        → ADK can query capabilities
    [DEGRADED if any component fails health check]
    STOPPING (on SIGTERM)
        → drain in-flight requests
        → stop plugins / unregister capabilities
        → disconnect Event Bus
    STOPPED

RuntimeState is the authoritative signal for:
    - Grafana dashboards
    - Langfuse observability
    - Kubernetes probes
    - Health endpoints
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from apps.runtime.src.domain.value_objects import RuntimeState, HealthStatus
from apps.runtime.src.domain.exceptions import RuntimeNotReadyError, EventBusError
from apps.runtime.src.ports.outbound import EventBusPort
from apps.runtime.src.application.context import ContextManager
from apps.runtime.src.application.capabilities import CapabilityRegistry

logger = logging.getLogger("astera.kernel")

# Platform version — bump on every release
PLATFORM_VERSION = "0.1.0"
PLATFORM_BUILD_DATE = "2026-08-07"


class AsteraKernel:
    """
    The Astera Platform Kernel.

    Manages the complete lifecycle of the platform:
        State Machine  → RuntimeState transitions (BOOTING → READY → ...)
        Context        → ContextManager (Org/Workspace/Encounter/Patient/Session)
        Event Bus      → EventBusPort (NATS)
        Plugin Registry→ dict of registered plugins (populated in Phase D)
        Capability Registry → CapabilityRegistry (Plugin → Capability 1:N)
        Health Manager → component health aggregation

    Nothing runs outside the Kernel. Everything is an extension of the Kernel.
    """

    def __init__(self, event_bus: EventBusPort) -> None:
        self._state = RuntimeState.BOOTING
        self._boot_time: float | None = None
        self._started_at: datetime | None = None

        # Core subsystems
        self._event_bus = event_bus
        self._context_manager = ContextManager()
        self._capability_registry = CapabilityRegistry()

        # Plugin Registry (raw dict — Plugin SDK will wrap this in Phase D)
        self._plugin_registry: dict[str, dict[str, Any]] = {}

        # Component health map
        self._component_health: dict[str, HealthStatus] = {
            "event_bus":           HealthStatus.UNKNOWN,
            "context_manager":     HealthStatus.UNKNOWN,
            "plugin_registry":     HealthStatus.UNKNOWN,
            "capability_registry": HealthStatus.UNKNOWN,
        }

    # ── Public Properties ─────────────────────────────────────────────────────

    @property
    def state(self) -> RuntimeState:
        """The current Kernel state. Source of truth for all observability."""
        return self._state

    @property
    def context(self) -> ContextManager:
        """Access to the Context Manager (sessions, encounters, patients)."""
        return self._context_manager

    @property
    def capabilities(self) -> CapabilityRegistry:
        """Access to the Capability Registry (what the platform can do)."""
        return self._capability_registry

    @property
    def uptime_seconds(self) -> float | None:
        if self._boot_time is None:
            return None
        return time.monotonic() - self._boot_time

    def is_ready(self) -> bool:
        return self._state.is_operational()

    # ── Bootstrap ─────────────────────────────────────────────────────────────

    async def startup(self) -> None:
        """
        Execute the Platform Bootstrap sequence.

        The Kernel transitions: BOOTING → READY (or FAILED on error).
        """
        logger.info("━" * 60)
        logger.info("  ASTERA KERNEL BOOTING")
        logger.info("━" * 60)
        t0 = time.monotonic()

        try:
            await self._step("event_bus",           self._connect_event_bus())
            await self._step("context_manager",     self._init_context_manager())
            await self._step("plugin_registry",     self._init_plugin_registry())
            await self._step("capability_registry", self._init_capability_registry())

            self._boot_time = time.monotonic()
            self._started_at = datetime.now(tz=timezone.utc)
            self._state = RuntimeState.READY

            elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
            logger.info("━" * 60)
            logger.info(
                "  ASTERA KERNEL READY",
                extra={"boot_time_ms": elapsed_ms, "version": PLATFORM_VERSION},
            )
            logger.info("━" * 60)

            await self._publish("astera.kernel.ready", {
                "event": "kernel.ready",
                "version": PLATFORM_VERSION,
                "boot_time_ms": elapsed_ms,
            })

        except Exception as exc:
            self._state = RuntimeState.FAILED
            logger.critical(
                "ASTERA KERNEL BOOT FAILED",
                extra={"error": str(exc)},
                exc_info=True,
            )
            raise

    async def shutdown(self) -> None:
        """Execute graceful shutdown. Kernel transitions: STOPPING → STOPPED."""
        if self._state.is_terminal():
            return

        logger.info("━" * 60)
        logger.info("  ASTERA KERNEL STOPPING")
        logger.info("━" * 60)
        self._state = RuntimeState.STOPPING

        try:
            await self._publish("astera.kernel.stopping", {"event": "kernel.stopping"})
            await self._teardown_plugins()
            await self._event_bus.disconnect()
        except Exception as exc:
            logger.warning("Non-fatal error during shutdown", extra={"error": str(exc)})
            self._state = RuntimeState.FAILED
            return

        self._state = RuntimeState.STOPPED
        logger.info("  ASTERA KERNEL STOPPED CLEANLY")
        logger.info("━" * 60)

    # ── Health & Introspection ────────────────────────────────────────────────

    async def get_health(self) -> dict[str, Any]:
        """Full health report. Called by /health/ready."""
        if not self.is_ready():
            raise RuntimeNotReadyError()

        return {
            "state":       self._state.value,
            "version":     PLATFORM_VERSION,
            "uptime_s":    round(self.uptime_seconds or 0, 1),
            "started_at":  self._started_at.isoformat() if self._started_at else None,
            "components":  {k: v.value for k, v in self._component_health.items()},
            "event_bus":   {"connected": await self._event_bus.is_connected()},
            "context":     self._context_manager.summary(),
            "capabilities": self._capability_registry.summary(),
            "plugins":     {"registered": len(self._plugin_registry)},
        }

    async def get_status(self) -> dict[str, Any]:
        """Lightweight status. Called by /status and liveness probes."""
        return {
            "state":    self._state.value,
            "ready":    self.is_ready(),
            "version":  PLATFORM_VERSION,
            "uptime_s": round(self.uptime_seconds or 0, 1),
        }

    def get_version_info(self) -> dict[str, Any]:
        """Build/version information for the /version endpoint."""
        return {
            "platform":    "astera",
            "version":     PLATFORM_VERSION,
            "build_date":  PLATFORM_BUILD_DATE,
            "kernel_state": self._state.value,
            "started_at":  self._started_at.isoformat() if self._started_at else None,
        }

    # ── Plugin Registry (raw — Plugin SDK wraps this in Phase D) ─────────────

    async def list_plugins(self) -> list[dict[str, Any]]:
        return list(self._plugin_registry.values())

    async def get_plugin(self, plugin_name: str) -> dict[str, Any]:
        from apps.runtime.src.domain.exceptions import PluginNotFoundError
        from apps.runtime.src.domain.value_objects import PluginName
        if plugin_name not in self._plugin_registry:
            raise PluginNotFoundError(PluginName(plugin_name))
        return self._plugin_registry[plugin_name]

    # ── Private: Bootstrap Steps ──────────────────────────────────────────────

    async def _step(self, component: str, coro) -> None:
        """Execute a bootstrap step, update component health, log result."""
        logger.info(f"  → {component}: initializing...")
        try:
            await coro
            self._component_health[component] = HealthStatus.HEALTHY
            logger.info(f"  ✓ {component}: ready")
        except Exception as exc:
            self._component_health[component] = HealthStatus.UNHEALTHY
            logger.error(f"  ✗ {component}: FAILED — {exc}")
            raise

    async def _connect_event_bus(self) -> None:
        await self._event_bus.connect()

    async def _init_context_manager(self) -> None:
        # ContextManager is initialized in __init__. Nothing async to do.
        # Placeholder for future: load active sessions from Redis.
        pass

    async def _init_plugin_registry(self) -> None:
        # Empty at Phase C. Plugin SDK populates this in Phase D.
        pass

    async def _init_capability_registry(self) -> None:
        # Empty at Phase C. Plugins register capabilities in Phase D.
        pass

    async def _teardown_plugins(self) -> None:
        if not self._plugin_registry:
            return
        logger.info(f"Stopping {len(self._plugin_registry)} plugins...")
        for name in list(self._plugin_registry):
            self._capability_registry.unregister_plugin(
                __import__(
                    "apps.runtime.src.domain.value_objects",
                    fromlist=["PluginName"],
                ).PluginName(name)
            )
        self._plugin_registry.clear()

    async def _publish(self, subject: str, payload: dict[str, Any]) -> None:
        """Publish a Kernel lifecycle event. Non-fatal on failure."""
        import json
        try:
            if await self._event_bus.is_connected():
                await self._event_bus.publish(
                    subject,
                    json.dumps(payload, default=str).encode(),
                )
        except Exception as exc:
            logger.warning(
                f"Could not publish '{subject}'",
                extra={"error": str(exc)},
            )
