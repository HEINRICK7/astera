"""EventBusError — raised when the Event Bus (NATS) encounters an error."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError


class EventBusError(AsteraError):
    """Raised on NATS connection or publish failures."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Event Bus error: {detail}", code="EVENT_BUS_ERROR")
