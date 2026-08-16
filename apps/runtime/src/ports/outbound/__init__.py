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
from typing import Any

from packages.shared.events import EventBusPort


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
