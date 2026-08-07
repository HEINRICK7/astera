"""
Astera Kernel — The Platform Operating System (v2).

Architecture (revised):

    AsteraKernel (OS — lifecycle, state, subsystems)
        ↓
    TaskOrchestrator (operational brain — decides who runs what)
        ↓
    CapabilityRegistry (what the platform CAN do)
        ↓
    ProviderRegistry + PluginResolver (who does it, how to call them)
        ↓
    Plugin (the concrete implementation — Phase D)

KEY RULE: The Kernel does NOT know Plugins.
    The Kernel knows Capabilities and Providers.
    The TaskOrchestrator knows the Resolver.
    The PluginResolver knows the Plugin instances.

When the ADK arrives in Phase D:
    adk.transcribe(audio) →
    orchestrator.execute(TaskIntent(SPEECH_TRANSCRIPTION, criteria)) →
    select_best() → Parakeet →
    plugin.invoke() → result
    ZERO changes to the Kernel.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from apps.runtime.src.domain.value_objects import RuntimeState, HealthStatus
from apps.runtime.src.domain.exceptions import RuntimeNotReadyError
from apps.runtime.src.ports.outbound import EventBusPort
from apps.runtime.src.application.context import ContextManager
from apps.runtime.src.application.capabilities import CapabilityRegistry
from apps.runtime.src.application.providers import ProviderRegistry, PluginResolver
from apps.runtime.src.application.orchestrator import TaskOrchestrator

logger = logging.getLogger("astera.kernel")

PLATFORM_VERSION = "0.1.0"
PLATFORM_BUILD_DATE = "2026-08-07"


class AsteraKernel:
    """
    The Astera Platform Kernel.

    Owns the lifecycle and provides subsystem access.
    Does NOT own Plugin instances (that is the PluginResolver's job).
    Does NOT decide which Provider to use (that is the Orchestrator's job).
    """

    def __init__(self, event_bus: EventBusPort) -> None:
        self._state = RuntimeState.BOOTING
        self._boot_time: float | None = None
        self._started_at: datetime | None = None

        # ── Subsystems (the Kernel's OS components) ───────────────────────────
        self._event_bus          = event_bus
        self._context_manager    = ContextManager()
        self._capability_registry = CapabilityRegistry()
        self._provider_registry   = ProviderRegistry()
        self._plugin_resolver     = PluginResolver()

        # ── Operational Brain ─────────────────────────────────────────────────
        # The TaskOrchestrator is wired by the Kernel but runs independently.
        self._orchestrator = TaskOrchestrator(
            capabilities=self._capability_registry,
            providers=self._provider_registry,
            resolver=self._plugin_resolver,
            event_bus=self._event_bus,
        )

        # Component health map (reported in /ready)
        self._component_health: dict[str, HealthStatus] = {
            "event_bus":          HealthStatus.UNKNOWN,
            "context_manager":    HealthStatus.UNKNOWN,
            "provider_registry":  HealthStatus.UNKNOWN,
            "capability_registry": HealthStatus.UNKNOWN,
            "task_orchestrator":  HealthStatus.UNKNOWN,
        }

    # ── Public Surface ────────────────────────────────────────────────────────

    @property
    def state(self) -> RuntimeState:
        return self._state

    @property
    def orchestrator(self) -> TaskOrchestrator:
        """The TaskOrchestrator. Used by HTTP adapters and the ADK."""
        return self._orchestrator

    @property
    def capabilities(self) -> CapabilityRegistry:
        return self._capability_registry

    @property
    def providers(self) -> ProviderRegistry:
        return self._provider_registry

    @property
    def context(self) -> ContextManager:
        return self._context_manager

    @property
    def uptime_seconds(self) -> float | None:
        return None if self._boot_time is None else time.monotonic() - self._boot_time

    def is_ready(self) -> bool:
        return self._state.is_operational()

    # ── Bootstrap ─────────────────────────────────────────────────────────────

    async def startup(self) -> None:
        logger.info("━" * 60)
        logger.info("  ASTERA KERNEL BOOTING")
        logger.info("━" * 60)
        t0 = time.monotonic()

        try:
            await self._step("event_bus",           self._connect_event_bus())
            await self._step("context_manager",     self._init_context_manager())
            await self._step("provider_registry",   self._init_provider_registry())
            await self._step("capability_registry", self._init_capability_registry())
            await self._step("task_orchestrator",   self._init_orchestrator())

            self._boot_time  = time.monotonic()
            self._started_at = datetime.now(tz=timezone.utc)
            self._state      = RuntimeState.READY

            elapsed_ms = round((time.monotonic() - t0) * 1000, 1)

            logger.info("━" * 60)
            logger.info(
                "  ASTERA KERNEL READY",
                extra={"boot_time_ms": elapsed_ms, "version": PLATFORM_VERSION},
            )
            logger.info("━" * 60)

            await self._publish("astera.kernel.ready", {
                "event":       "kernel.ready",
                "version":     PLATFORM_VERSION,
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
        if self._state.is_terminal():
            return

        logger.info("━" * 60)
        logger.info("  ASTERA KERNEL STOPPING")
        logger.info("━" * 60)
        self._state = RuntimeState.STOPPING

        try:
            await self._publish("astera.kernel.stopping", {"event": "kernel.stopping"})
            await self._teardown_providers()
            await self._event_bus.disconnect()
        except Exception as exc:
            logger.warning("Non-fatal error during shutdown", extra={"error": str(exc)})
            self._state = RuntimeState.FAILED
            return

        self._state = RuntimeState.STOPPED
        logger.info("  ASTERA KERNEL STOPPED CLEANLY")
        logger.info("━" * 60)

    # ── Health & Introspection (implements KernelPort) ────────────────────────

    async def get_health(self) -> dict[str, Any]:
        if not self.is_ready():
            raise RuntimeNotReadyError()
        return {
            "state":        self._state.value,
            "version":      PLATFORM_VERSION,
            "uptime_s":     round(self.uptime_seconds or 0, 1),
            "started_at":   self._started_at.isoformat() if self._started_at else None,
            "components":   {k: v.value for k, v in self._component_health.items()},
            "event_bus":    {"connected": await self._event_bus.is_connected()},
            "context":      self._context_manager.summary(),
            "capabilities": self._capability_registry.summary(),
            "providers":    self._provider_registry.summary(),
        }

    async def get_status(self) -> dict[str, Any]:
        return {
            "state":    self._state.value,
            "ready":    self.is_ready(),
            "version":  PLATFORM_VERSION,
            "uptime_s": round(self.uptime_seconds or 0, 1),
        }

    def get_version_info(self) -> dict[str, Any]:
        return {
            "platform":     "astera",
            "version":      PLATFORM_VERSION,
            "build_date":   PLATFORM_BUILD_DATE,
            "kernel_state": self._state.value,
            "started_at":   self._started_at.isoformat() if self._started_at else None,
        }

    # ── Private: Bootstrap Steps ──────────────────────────────────────────────

    async def _step(self, component: str, coro) -> None:
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
        pass  # Scaffold: Phase D loads active sessions from Redis

    async def _init_provider_registry(self) -> None:
        pass  # Scaffold: Phase D plugins register here on startup

    async def _init_capability_registry(self) -> None:
        pass  # Scaffold: Phase D plugins register CapabilityDescriptors here

    async def _init_orchestrator(self) -> None:
        pass  # Orchestrator is wired in __init__, nothing async to initialize

    async def _teardown_providers(self) -> None:
        """Gracefully unregister all providers on shutdown."""
        providers = self._provider_registry.list_all()
        if not providers:
            return
        logger.info(f"Stopping {len(providers)} providers...")
        for provider in providers:
            self._plugin_resolver.unbind(provider.name)
            self._capability_registry.unregister_provider(provider.name)
        self._provider_registry.list_all().clear()

    async def _publish(self, subject: str, payload: dict[str, Any]) -> None:
        import json
        try:
            if await self._event_bus.is_connected():
                await self._event_bus.publish(
                    subject,
                    json.dumps(payload, default=str).encode(),
                )
        except Exception as exc:
            logger.warning(f"Could not publish '{subject}'", extra={"error": str(exc)})
