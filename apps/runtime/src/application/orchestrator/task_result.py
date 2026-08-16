"""
TaskResult — outcome of a TaskOrchestrator.execute() call.

WHY a frozen dataclass (not a dict):
    Results are value objects. They carry outcome, not mutable state.
    Immutability makes results safe to pass across boundaries (API, EventBus, tests).
    to_event_payload() encapsulates the serialization concern.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from apps.runtime.src.domain.value_objects.capability_type import CapabilityType


@dataclass(frozen=True)
class TaskResult:
    """
    The outcome of a TaskOrchestrator.execute() call.

    Published to the Event Bus as:
        astera.task.completed  (success=True)
        astera.task.failed     (success=False)

    Returned directly to the ADK / API caller.
    """

    request_id: str
    capability_type: CapabilityType
    success: bool

    provider_name: str | None = None
    plugin_name: str | None = None
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 0.0
    executed_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    def to_event_payload(self) -> dict[str, Any]:
        """Serialize for Event Bus publication."""
        return {
            "request_id":      self.request_id,
            "capability_type": self.capability_type.value,
            "success":         self.success,
            "provider":        self.provider_name,
            "plugin":          self.plugin_name,
            "latency_ms":      self.latency_ms,
            "output":          self.output,
            "error":           self.error,
            "executed_at":     self.executed_at.isoformat(),
        }
