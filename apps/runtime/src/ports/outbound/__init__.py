"""
Astera Runtime — Outbound Ports (Secondary/Driven Ports).

Outbound ports define HOW the application reaches external systems.
They are pure interfaces (ABCs) — the application core depends on these,
NOT on concrete infrastructure implementations.

Adapters (NATS, PostgreSQL, etc.) implement these ports.

Rule: The application layer calls outbound ports.
      Adapters implement outbound ports.
      The application NEVER imports adapters directly.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable


class EventBusPort(ABC):
    """
    Outbound port for the Event Bus.

    The application publishes and subscribes to events through this interface.
    The concrete adapter (NatsEventBusAdapter) implements this for NATS.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the Event Bus."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully disconnect from the Event Bus."""
        ...

    @abstractmethod
    async def publish(self, subject: str, payload: bytes) -> None:
        """
        Publish a message to a subject.

        Args:
            subject: NATS subject (e.g., 'astera.runtime.started').
            payload: Raw bytes payload (typically JSON-encoded).
        """
        ...

    @abstractmethod
    async def subscribe(
        self,
        subject: str,
        handler: Callable[[bytes], Awaitable[None]],
    ) -> None:
        """
        Subscribe to a subject with an async handler.

        Args:
            subject: NATS subject pattern (supports wildcards: *, >).
            handler: Async callable invoked for each received message.
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Return True if the Event Bus connection is alive."""
        ...


class HealthRepositoryPort(ABC):
    """
    Outbound port for persisting and retrieving health snapshots.

    Optional — the Runtime can operate without persisting health data.
    """

    @abstractmethod
    async def save_health_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Persist a health snapshot for historical analysis."""
        ...

    @abstractmethod
    async def get_latest_health(self) -> dict[str, Any] | None:
        """Retrieve the most recent health snapshot."""
        ...
