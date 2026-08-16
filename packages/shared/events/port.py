"""Shared Event Bus SDK contract.

This module is deliberately free of NATS, FastAPI, and infrastructure imports.
Adapters implement the contract; application modules depend only on this port.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from pydantic import BaseModel

EventHandler = Callable[[bytes], Awaitable[None]]


class EventPublisher(ABC):
    """Outbound contract for publishing serialized events."""

    @abstractmethod
    async def publish(self, subject: str, payload: bytes) -> None:
        """Publish a serialized event to a subject."""
        ...


class EventSubscriber(ABC):
    """Outbound contract for subscribing async handlers to subjects."""

    @abstractmethod
    async def subscribe(self, subject: str, handler: EventHandler) -> None:
        """Register an async handler for a subject pattern."""
        ...


class EventBusPort(EventPublisher, EventSubscriber):
    """Complete lifecycle, publishing, and subscription contract."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish the broker connection."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the broker connection gracefully."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Return whether the broker connection is currently usable."""
        ...


def serialize_event(event: BaseModel) -> bytes:
    """Serialize a shared event model using its canonical JSON representation."""
    return event.model_dump_json().encode("utf-8")
