"""
Astera Kernel — Task Orchestrator.

The TaskOrchestrator is the OPERATIONAL BRAIN of the Astera platform.

The AsteraKernel is the OPERATING SYSTEM (lifecycle, state, subsystems).
The TaskOrchestrator is the SCHEDULER (decides what runs, how, and with whom).

They are intentionally separate:
    AsteraKernel     → "Is the platform alive and healthy?"
    TaskOrchestrator → "Which provider handles this intent? Execute it."

Execution flow:
    ADK / API sends: TaskIntent(
        capability_type = CapabilityType.SPEECH_TRANSCRIPTION,
        payload         = <audio bytes>,
        criteria        = SelectionCriteria(language="pt-BR", requires_streaming=True),
        context         = ContextScope(encounter_id="enc-123", patient_id="pat-456"),
    )

    TaskOrchestrator:
        1. Asks CapabilityRegistry: "Who is the best SPEECH_TRANSCRIPTION in pt-BR + streaming?"
           → CapabilityDescriptor(provider=ProviderName("parakeet"), ...)

        2. Asks ProviderRegistry: "Give me the Provider entity for Parakeet."
           → Provider(name="parakeet", plugin=PluginName("speech-plugin"), ...)

        3. Asks PluginResolver: "Give me the Plugin instance for Parakeet."
           → PluginProtocol (Phase D: concrete SpeechPlugin instance)

        4. Calls: plugin.invoke(provider, capability, payload, context.to_dict())
           → {"transcript": "...", "confidence": 0.98, "language": "pt-BR"}

        5. Publishes: astera.task.completed event via EventBus

        6. Returns: TaskResult(success=True, provider="parakeet", output={...})

Phase C status:
    Steps 1–3 are fully implemented.
    Step 4 raises NotImplementedError → Phase D (Plugin SDK) will complete this.
    Step 5 publishes a stub event.
    Step 6 returns a TaskResult with success=False and error="Phase D: no plugins loaded."
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from apps.runtime.src.domain.entities import ContextScope
from apps.runtime.src.domain.value_objects import (
    CapabilityType,
    PluginName,
    ProviderName,
    SelectionCriteria,
)
from apps.runtime.src.domain.exceptions import (
    CapabilityNotFoundError,
    NoHealthyProviderError,
    RuntimeNotReadyError,
)
from apps.runtime.src.application.capabilities import CapabilityRegistry
from apps.runtime.src.application.providers import ProviderRegistry, PluginResolver
from apps.runtime.src.ports.outbound import EventBusPort

logger = logging.getLogger("astera.task_orchestrator")


# ── Task Intent ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TaskIntent:
    """
    A request from the ADK (or API) to the TaskOrchestrator.

    The caller declares WHAT they need and the constraints.
    The Orchestrator decides WHO handles it.

    The ADK never names a Provider or Plugin.
    The caller never names a Provider or Plugin.
    """

    capability_type: CapabilityType
    payload: Any                                # audio bytes, image bytes, text, dict…
    context: ContextScope
    criteria: SelectionCriteria = field(default_factory=SelectionCriteria)
    request_id: str = field(default_factory=lambda: __import__("uuid").uuid4().hex)


# ── Task Result ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TaskResult:
    """
    The outcome of a TaskOrchestrator.execute() call.

    Published to the Event Bus as astera.task.completed (or .failed).
    Returned directly to the ADK / API caller.
    """

    request_id: str
    capability_type: CapabilityType
    success: bool

    # Who handled this (filled when a provider was selected)
    provider_name: str | None = None
    plugin_name: str | None = None

    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 0.0
    executed_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    def to_event_payload(self) -> dict[str, Any]:
        return {
            "request_id":      self.request_id,
            "capability_type": self.capability_type.value,
            "success":         self.success,
            "provider":        self.provider_name,
            "plugin":          self.plugin_name,
            "latency_ms":      self.latency_ms,
            "error":           self.error,
            "executed_at":     self.executed_at.isoformat(),
        }


# ── Task Orchestrator ─────────────────────────────────────────────────────────

class TaskOrchestrator:
    """
    The operational brain of the Astera platform.

    Responsibilities:
        - Receive a TaskIntent (from ADK, API, or test)
        - Select the best Provider via CapabilityRegistry.select_best()
        - Resolve the Plugin via PluginResolver
        - Invoke the Plugin
        - Publish the result event via EventBus
        - Return a TaskResult

    Dependencies (injected, never imported directly):
        CapabilityRegistry  → what the platform can do
        ProviderRegistry    → who can do it (metadata + status)
        PluginResolver      → how to call them (Plugin instances)
        EventBusPort        → where to publish results
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
        """
        Execute a TaskIntent end-to-end.

        Phase C: Steps 1–3 are complete. Step 4 (plugin.invoke) is a Phase D stub.
        """
        t0 = time.monotonic()
        logger.info(
            "Task intent received",
            extra={
                "request_id":      intent.request_id,
                "capability_type": intent.capability_type.value,
                "has_criteria":    not intent.criteria.is_empty(),
                "context_id":      intent.context.id,
            },
        )

        try:
            # ── Step 1: Select best Provider via CapabilityRegistry ────────────
            descriptor = self._capabilities.select_best(
                intent.capability_type,
                intent.criteria,
            )
            logger.info(
                "Provider selected",
                extra={
                    "provider": str(descriptor.provider),
                    "plugin":   str(descriptor.plugin),
                },
            )

            # ── Step 2: Verify Provider is registered in ProviderRegistry ──────
            provider = self._providers.get(descriptor.provider)

            # ── Step 3: Resolve Plugin via PluginResolver ─────────────────────
            plugin = self._resolver.resolve(descriptor.provider)

            # ── Step 4: Invoke Plugin ─────────────────────────────────────────
            #
            # PHASE D PLACEHOLDER
            # The Plugin SDK will implement plugin.invoke() here.
            # The interface is already defined in PluginProtocol.
            #
            output = await plugin.invoke(
                provider=descriptor.provider,
                capability=intent.capability_type,
                payload=intent.payload,
                context=intent.context.to_dict(),
            )

            latency_ms = round((time.monotonic() - t0) * 1000, 2)

            result = TaskResult(
                request_id=intent.request_id,
                capability_type=intent.capability_type,
                success=True,
                provider_name=str(descriptor.provider),
                plugin_name=str(descriptor.plugin),
                output=output,
                latency_ms=latency_ms,
            )

        except NotImplementedError as exc:
            # Phase C — Plugin SDK not yet loaded. Return a structured stub result.
            latency_ms = round((time.monotonic() - t0) * 1000, 2)
            logger.warning(
                "Task execution deferred (Phase D)",
                extra={
                    "request_id": intent.request_id,
                    "reason":     str(exc),
                },
            )
            result = TaskResult(
                request_id=intent.request_id,
                capability_type=intent.capability_type,
                success=False,
                error="[Phase D] Plugin SDK not yet loaded. No providers are bound.",
                latency_ms=latency_ms,
            )

        except (CapabilityNotFoundError, NoHealthyProviderError) as exc:
            latency_ms = round((time.monotonic() - t0) * 1000, 2)
            logger.warning(
                "No provider available for task",
                extra={
                    "request_id": intent.request_id,
                    "error":      str(exc),
                },
            )
            result = TaskResult(
                request_id=intent.request_id,
                capability_type=intent.capability_type,
                success=False,
                error=str(exc),
                latency_ms=latency_ms,
            )

        # ── Step 5: Publish result event ──────────────────────────────────────
        await self._publish_result(result)

        return result

    async def _publish_result(self, result: TaskResult) -> None:
        """Publish task result to the Event Bus. Non-fatal on failure."""
        import json
        subject = "astera.task.completed" if result.success else "astera.task.failed"
        try:
            if await self._event_bus.is_connected():
                await self._event_bus.publish(
                    subject,
                    json.dumps(result.to_event_payload(), default=str).encode(),
                )
        except Exception as exc:
            logger.warning(
                f"Could not publish '{subject}'",
                extra={"error": str(exc)},
            )

    # ── Introspection ─────────────────────────────────────────────────────────

    async def list_available_intents(self, language: str | None = None) -> list[dict[str, Any]]:
        """
        What can the ADK ask the Orchestrator to do?

        Returns all capabilities the platform can currently handle,
        optionally filtered by language.
        """
        descriptors = self._capabilities.query(language=language)
        return [d.to_summary() for d in descriptors]
