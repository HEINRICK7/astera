"""EventBusNotConnectedError — raised when the bus is used before connection."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError


class EventBusNotConnectedError(AsteraError):
    """Raised when publishing or subscribing without an active bus connection."""

    def __init__(self) -> None:
        super().__init__(
            "Event Bus is not connected.",
            code="EVENT_BUS_NOT_CONNECTED",
        )
