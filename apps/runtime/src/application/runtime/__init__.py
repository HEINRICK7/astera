"""
Astera Runtime — Application Layer: Runtime Use Cases.

The RuntimeManager is the central application service that orchestrates
the entire Platform Bootstrap sequence:

    Startup → Configuration → Container → EventBus → PluginRegistry
    → HealthManager → LifecycleManager → API Ready

This is the heart of the Astera Runtime.
No HTTP. No NATS. No FastAPI. Pure application logic.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from apps.runtime.src.domain.value_objects import RuntimeStatus, HealthStatus
from apps.runtime.src.domain.exceptions import (
    RuntimeNotReadyError,
    EventBusNotConnectedError,
)
from apps.runtime.src.ports.outbound import EventBusPort

logger = logging.getLogger("astera.runtime.manager")


class RuntimeManager:
    """
    Central orchestrator of the Astera Runtime lifecycle.

    Responsibilities:
    - Manage the startup sequence (Platform Bootstrap)
    - Track overall runtime status
    - Coordinate graceful shutdown
    - Expose health information to inbound adapters

    This class does NOT:
    - Know about HTTP
    - Import FastAPI, NATS, or any infrastructure
    - Contain any business domain logic (clinical, medical, etc.)
    """

    def __init__(self, event_bus: EventBusPort) -> None:
        self._event_bus = event_bus
        self._status = RuntimeStatus.INITIALIZING
        self._component_health: dict[str, HealthStatus] = {}
        self._startup_time: float | None = None
        self._plugin_registry: dict[str, dict[str, Any]] = {}

    # ── Status ────────────────────────────────────────────────────────────────

    @property
    def status(self) -> RuntimeStatus:
        return self._status

    def is_ready(self) -> bool:
        return self._status.can_accept_requests()

    # ── Startup ───────────────────────────────────────────────────────────────

    async def startup(self) -> None:
        """
        Execute the Platform Bootstrap sequence.

        This method is called once during process startup.
        It must complete successfully for the Runtime to accept requests.
        """
        import time

        logger.info("Astera Runtime startup initiated", extra={"status": self._status})
        self._status = RuntimeStatus.STARTING
        start = time.monotonic()

        try:
            await self._connect_event_bus()
            await self._initialize_plugin_registry()
            await self._initialize_health_manager()

            self._startup_time = time.monotonic() - start
            self._status = RuntimeStatus.RUNNING

            logger.info(
                "Astera Runtime startup complete",
                extra={
                    "status": self._status,
                    "startup_time_ms": round(self._startup_time * 1000, 2),
                    "plugins_registered": len(self._plugin_registry),
                },
            )

            # Announce to the Event Bus that the Runtime is ready
            await self._publish_runtime_started()

        except Exception as exc:
            self._status = RuntimeStatus.DEGRADED
            logger.error(
                "Astera Runtime startup failed",
                extra={"error": str(exc), "status": self._status},
                exc_info=True,
            )
            raise

    # ── Shutdown ──────────────────────────────────────────────────────────────

    async def shutdown(self) -> None:
        """
        Execute graceful shutdown sequence.

        Called on SIGTERM/SIGINT. Drains in-flight requests,
        stops plugins, disconnects from the Event Bus.
        """
        logger.info("Astera Runtime shutdown initiated", extra={"status": self._status})
        self._status = RuntimeStatus.STOPPING

        try:
            await self._shutdown_plugins()
            await self._event_bus.disconnect()
        except Exception as exc:
            logger.warning(
                "Non-fatal error during shutdown",
                extra={"error": str(exc)},
            )
        finally:
            self._status = RuntimeStatus.STOPPED
            logger.info("Astera Runtime stopped cleanly")

    # ── Health ────────────────────────────────────────────────────────────────

    async def get_status(self) -> dict[str, Any]:
        """Return a summary of the current Runtime status."""
        return {
            "status": self._status.value,
            "ready": self.is_ready(),
            "startup_time_ms": round(self._startup_time * 1000, 2) if self._startup_time else None,
            "plugins_registered": len(self._plugin_registry),
        }

    async def get_health(self) -> dict[str, Any]:
        """Return a detailed health report of all platform components."""
        if not self.is_ready():
            raise RuntimeNotReadyError()

        return {
            "runtime": self._status.value,
            "components": {
                name: status.value
                for name, status in self._component_health.items()
            },
            "event_bus": {
                "connected": await self._event_bus.is_connected(),
            },
            "plugins": list(self._plugin_registry.keys()),
        }

    # ── Plugin Registry ───────────────────────────────────────────────────────

    async def list_plugins(self) -> list[dict[str, Any]]:
        return list(self._plugin_registry.values())

    async def get_plugin(self, plugin_name: str) -> dict[str, Any]:
        from apps.runtime.src.domain.exceptions import PluginNotFoundError
        if plugin_name not in self._plugin_registry:
            raise PluginNotFoundError(plugin_name)
        return self._plugin_registry[plugin_name]

    # ── Private: Bootstrap Steps ──────────────────────────────────────────────

    async def _connect_event_bus(self) -> None:
        logger.info("Connecting to Event Bus (NATS)...")
        await self._event_bus.connect()
        self._component_health["event_bus"] = HealthStatus.HEALTHY
        logger.info("Event Bus connected")

    async def _initialize_plugin_registry(self) -> None:
        logger.info("Initializing Plugin Registry...")
        # At this stage, no plugins are loaded. The registry is empty.
        # Plugins will be discovered and registered in Phase D.
        self._component_health["plugin_registry"] = HealthStatus.HEALTHY
        logger.info("Plugin Registry initialized (0 plugins)")

    async def _initialize_health_manager(self) -> None:
        logger.info("Initializing Health Manager...")
        self._component_health["health_manager"] = HealthStatus.HEALTHY
        logger.info("Health Manager initialized")

    async def _publish_runtime_started(self) -> None:
        """Publish a 'runtime.started' event to notify any listeners."""
        import json
        from datetime import datetime, timezone

        payload = json.dumps({
            "event_type": "runtime.started",
            "version": "1.0",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }).encode()

        try:
            await self._event_bus.publish("astera.runtime.started", payload)
            logger.info("Published 'astera.runtime.started' event")
        except Exception as exc:
            # Non-fatal: log and continue
            logger.warning(
                "Could not publish runtime.started event",
                extra={"error": str(exc)},
            )

    async def _shutdown_plugins(self) -> None:
        """Stop all registered plugins gracefully."""
        if not self._plugin_registry:
            return
        logger.info("Stopping plugins...", extra={"count": len(self._plugin_registry)})
        # Plugin shutdown logic will be implemented in Phase D (Plugin SDK)
        self._plugin_registry.clear()
        logger.info("All plugins stopped")
