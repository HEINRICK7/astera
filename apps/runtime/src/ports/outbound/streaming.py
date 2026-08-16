"""Outbound port for publishing and subscribing to runtime stream events."""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from packages.streaming_sdk import StreamEvent


@runtime_checkable
class StreamBrokerPort(Protocol):
    """Application-facing stream broker contract."""

    async def publish(self, event: StreamEvent) -> None:
        """Publish one event to subscribers for its stream."""
        ...

    def subscribe(self, stream_id: str) -> AsyncIterator[StreamEvent]:
        """Subscribe to the ordered events of one stream."""
        ...
