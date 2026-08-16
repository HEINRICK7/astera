"""Development stream broker adapter for the Runtime composition root."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from apps.runtime.src.ports.outbound.streaming import StreamBrokerPort
from packages.streaming_sdk import StreamEvent


class InMemoryStreamBrokerAdapter(StreamBrokerPort):
    """Publish ordered events to concurrent subscribers in local deployments."""

    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[StreamEvent]]] = {}

    async def publish(self, event: StreamEvent) -> None:
        for queue in tuple(self._subscribers.get(event.stream_id, ())):
            await queue.put(event)

    async def subscribe(self, stream_id: str) -> AsyncIterator[StreamEvent]:
        queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        self._subscribers.setdefault(stream_id, set()).add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._subscribers.get(stream_id, set()).discard(queue)
