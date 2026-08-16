"""
TaskOrchestrator — the operational brain of the Astera platform.

WHY separated from AsteraKernel:
    AsteraKernel = the OS (lifecycle, state, subsystems).
    TaskOrchestrator = the scheduler (decides what runs, how, and with whom).
    Clear separation of concerns. Each can evolve independently.
    The Kernel can restart without the Orchestrator losing its wiring.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.orchestrator.task_intent import TaskIntent
from apps.runtime.src.application.orchestrator.task_result import TaskResult
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.exceptions.capability_not_found import CapabilityNotFoundError
from apps.runtime.src.domain.exceptions.no_healthy_provider import NoHealthyProviderError
from apps.runtime.src.ports.outbound import EventBusPort

logger = logging.getLogger("astera.task_orchestrator")

_PHASE_D_STUB = "[Phase D] Plugin SDK not yet loaded. No providers are bound."


class TaskOrchestrator:
    """
    Receives a TaskIntent → selects Provider → invokes Plugin → publishes result.

    Execution flow:
        1. CapabilityRegistry.select_best() → CapabilityDescriptor
        2. ProviderRegistry.get()           → Provider entity
        3. PluginResolver.resolve()         → PluginProtocol instance
        4. plugin.invoke()                  → output dict   [Phase D]
        5. EventBus.publish()               → astera.task.completed
        6. Return TaskResult
    """

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
        resolver: PluginResolver,
        event_bus: EventBusPort,
    ) -> None:
        self._capabilities = capabilities
        self._providers    = providers
        self._resolver     = resolver
        self._event_bus    = event_bus

    async def execute(self, intent: TaskIntent) -> TaskResult:
        t0 = time.monotonic()
        logger.info("Task intent received", extra={
            "request_id":      intent.request_id,
            "capability_type": intent.capability_type.value,
        })

        try:
            descriptor = self._capabilities.select_best(intent.capability_type, intent.criteria)
            self._providers.get(descriptor.provider)  # verify provider is known
            plugin = self._resolver.resolve(descriptor.provider)

            output = await plugin.invoke(
                provider=descriptor.provider,
                capability=intent.capability_type,
                payload=intent.payload,
                context=intent.context.to_dict(),
            )

            result = TaskResult(
                request_id=intent.request_id,
                capability_type=intent.capability_type,
                success=True,
                provider_name=str(descriptor.provider),
                plugin_name=str(descriptor.plugin),
                output=output,
                latency_ms=round((time.monotonic() - t0) * 1000, 2),
            )

        except NotImplementedError:
            result = TaskResult(
                request_id=intent.request_id,
                capability_type=intent.capability_type,
                success=False,
                error=_PHASE_D_STUB,
                latency_ms=round((time.monotonic() - t0) * 1000, 2),
            )

        except (CapabilityNotFoundError, NoHealthyProviderError) as exc:
            result = TaskResult(
                request_id=intent.request_id,
                capability_type=intent.capability_type,
                success=False,
                error=str(exc),
                latency_ms=round((time.monotonic() - t0) * 1000, 2),
            )

        await self._publish_result(result)
        return result

    async def list_available_intents(self, language: str | None = None) -> list[dict[str, Any]]:
        """ADK discovery: what can the Orchestrator handle right now?"""
        return [d.to_summary() for d in self._capabilities.query(language=language)]

    async def _publish_result(self, result: TaskResult) -> None:
        subject = "astera.task.completed" if result.success else "astera.task.failed"
        try:
            if await self._event_bus.is_connected():
                await self._event_bus.publish(
                    subject,
                    json.dumps(result.to_event_payload(), default=str).encode(),
                )
        except Exception as exc:
            logger.warning(f"Could not publish '{subject}'", extra={"error": str(exc)})
