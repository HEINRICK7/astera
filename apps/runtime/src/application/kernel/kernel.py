"""
AsteraKernel — the OS of the Astera platform.

WHY AsteraKernel and not RuntimeManager:
    A Manager manages.
    A Kernel orchestrates the platform's own existence.
    It governs the lifecycle, the state machine, and the subsystem startup order.
    Nothing runs before the Kernel says so.

Responsibilities:
    1. Boot sequence (ordered subsystem startup).
    2. State machine (BOOTING → READY → STOPPING → STOPPED).
    3. Wire subsystems together (CapabilityRegistry, ProviderRegistry, Orchestrator).
    4. Graceful shutdown (reverse order teardown).
    5. Health reporting.

NOT responsible for:
    - Scoring providers (CapabilityScorer)
    - Executing tasks (TaskOrchestrator)
    - Plugin lifecycle (Phase D Plugin SDK)
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from apps.runtime.src.application.capabilities.catalog import CapabilityCatalog
from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.context.manager import ContextManager
from apps.runtime.src.application.orchestrator.orchestrator import TaskOrchestrator
from apps.runtime.src.application.orchestrator.task_intent import TaskIntent
from apps.runtime.src.application.orchestrator.task_result import TaskResult
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.runtime_state import RuntimeState
from apps.runtime.src.ports.outbound import EventBusPort
from apps.runtime.src.domain.exceptions.runtime_not_ready import RuntimeNotReadyError
from packages.plugin_sdk import PluginRegistry
from packages.shared.observability import NoopObservability, ObservabilityPort

logger = logging.getLogger("astera.kernel")


class AsteraKernel:
    """
    The Operating System of the Astera platform.

    Usage:
        kernel = AsteraKernel(event_bus)
        await kernel.start()
        # ... serve requests ...
        await kernel.stop()
    """

    def __init__(
        self,
        event_bus: EventBusPort,
        observability: ObservabilityPort | None = None,
    ) -> None:
        self._state    = RuntimeState.BOOTING
        self._event_bus = event_bus
        self._observability = observability or NoopObservability()
        self._boot_time: float | None = None
        self._started_at: datetime | None = None

        # Subsystems — constructed once and wired into the orchestrator.
        self._context = ContextManager()
        self._capabilities = CapabilityRegistry()
        self._capability_catalog = CapabilityCatalog(self._capabilities)
        self._providers = ProviderRegistry()
        self._resolver = PluginResolver()
        self._plugins = PluginRegistry()
        self._orchestrator = TaskOrchestrator(
            capabilities=self._capabilities,
            providers=self._providers,
            resolver=self._resolver,
            event_bus=self._event_bus,
        )

    # ─── Public API ───────────────────────────────────────────────────────────

    async def startup(self) -> None:
        """Boot sequence. Call once. Raises on failure."""
        if self._state.is_operational():
            return
        logger.info("Kernel boot started")
        try:
            with self._observability.span("astera.kernel.startup"):
                await self._event_bus.connect()
                await self._plugins.start_all()
            self._boot_time = time.monotonic()
            self._started_at = datetime.now(tz=timezone.utc)
            self._state = RuntimeState.READY
            logger.info("Kernel READY", extra={"state": self._state.value})
            await self._publish("astera.kernel.ready", {
                "event": "kernel.ready",
                "started_at": self._started_at.isoformat(),
            })
            self._observability.increment_counter("astera.kernel.startups")
        except Exception as exc:
            self._state = RuntimeState.FAILED
            logger.critical("Kernel FAILED during boot", exc_info=exc)
            raise

    async def shutdown(self) -> None:
        """Graceful shutdown. Always completes."""
        if self._state == RuntimeState.STOPPED:
            return
        self._state = RuntimeState.STOPPING
        logger.info("Kernel STOPPING")
        try:
            await self._publish("astera.kernel.stopping", {"event": "kernel.stopping"})
            await self._plugins.stop_all()
            for provider in self._providers.list_all():
                self._resolver.unbind(provider.name)
                self._capabilities.unregister_provider(provider.name)
                self._providers.unregister(provider.name)
            await self._event_bus.disconnect()
        finally:
            self._state = RuntimeState.STOPPED
            shutdown = getattr(self._observability, "shutdown", None)
            if shutdown:
                shutdown()
            logger.info("Kernel STOPPED")

    async def start(self) -> None:
        """Compatibility alias for callers using the shorter lifecycle name."""
        await self.startup()

    async def stop(self) -> None:
        """Compatibility alias for callers using the shorter lifecycle name."""
        await self.shutdown()

    @property
    def state(self) -> RuntimeState:
        return self._state

    @property
    def providers(self) -> ProviderRegistry:
        return self._providers

    @property
    def resolver(self) -> PluginResolver:
        return self._resolver

    @property
    def plugins(self) -> PluginRegistry:
        return self._plugins

    @property
    def context(self) -> ContextManager:
        return self._context

    @property
    def uptime_seconds(self) -> float | None:
        if self._boot_time is None:
            return None
        return time.monotonic() - self._boot_time

    def is_ready(self) -> bool:
        return self._state.is_operational()

    @property
    def orchestrator(self) -> TaskOrchestrator:
        if not self._state.is_operational():
            raise RuntimeError("Kernel not ready. Call start() first.")
        return self._orchestrator

    @property
    def capabilities(self) -> CapabilityRegistry:
        return self._capabilities

    @property
    def capability_catalog(self) -> CapabilityCatalog:
        """Provider-neutral capability discovery for ADK and orchestration."""
        return self._capability_catalog

    async def execute_task(self, intent: TaskIntent) -> TaskResult:
        """Execute a task through the inbound API boundary."""
        if not self.is_ready():
            raise RuntimeNotReadyError()
        return await self._orchestrator.execute(intent)

    async def list_plugins(self) -> list[dict[str, Any]]:
        return self._plugins.list_all()

    async def get_plugin(self, plugin_name: str) -> dict[str, Any]:
        return self._plugins.get_summary(plugin_name)

    async def get_status(self) -> dict[str, Any]:
        return {
            "state": self._state.value,
            "ready": self.is_ready(),
            "uptime_s": round(self.uptime_seconds or 0, 1),
        }

    async def get_health(self) -> dict[str, Any]:
        return {
            **await self.get_status(),
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "event_bus": {"connected": await self._event_bus.is_connected()},
            "context": self._context.summary(),
            "capabilities": self._capabilities.summary(),
            "providers": self._providers.summary(),
            "plugins": self._plugins.summary(),
        }

    def get_version_info(self) -> dict[str, Any]:
        return {
            "platform": "astera",
            "version": "0.1.0",
            "build_date": "2026-08-07",
            "kernel_state": self._state.value,
        }

    def health(self) -> dict[str, Any]:
        return {
            "state":       self._state.value,
            "operational": self._state.is_operational(),
            "capabilities": self._capabilities.summary(),
            "providers": self._providers.summary(),
            "plugins": self._plugins.summary(),
        }

    async def _publish(self, subject: str, payload: dict[str, Any]) -> None:
        """Best-effort lifecycle publication; shutdown must remain reliable."""
        try:
            if await self._event_bus.is_connected():
                import json
                await self._event_bus.publish(subject, json.dumps(payload).encode())
        except Exception as exc:
            logger.warning("Could not publish lifecycle event", extra={"error": str(exc)})
