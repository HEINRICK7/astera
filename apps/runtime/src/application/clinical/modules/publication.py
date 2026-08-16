"""Ordered clinical event publication and review projection."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from packages.streaming_sdk import StreamEvent
from apps.runtime.src.ports.outbound.persistence import ReviewRepositoryPort
from apps.runtime.src.ports.outbound.streaming import StreamBrokerPort

logger = logging.getLogger("astera.clinical.publication")


class ClinicalPublicationModule:
    """Serialize stream events and asynchronously project them to review."""

    def __init__(self, *, broker: StreamBrokerPort, review_store: ReviewRepositoryPort, stream_id: str) -> None:
        self._broker = broker
        self._review_store = review_store
        self._stream_id = stream_id
        self._sequence = 0
        self._lock = asyncio.Lock()
        self._review_queue: asyncio.Queue[StreamEvent | None] = asyncio.Queue()
        self._review_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self._review_task = asyncio.create_task(self._project_review())

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        logger.info(
            "clinical.stream event=%s stream_id=%s sequence=%s",
            event_type,
            self._stream_id,
            self._sequence,
        )
        async with self._lock:
            event = StreamEvent(
                stream_id=self._stream_id,
                event_type=event_type,
                sequence=self._sequence,
                payload=payload,
            )
            self._sequence += 1
            await self._broker.publish(event)
            await self._review_queue.put(event)

    async def publish_a2ui(self, operations: tuple[dict[str, Any], ...]) -> None:
        if not operations:
            return
        await self.publish(
            "a2ui.cognitive.stream",
            {
                "protocol": "astera-workspace-state/1",
                "content_type": "application/jsonl",
                "jsonl": "\n".join(
                    json.dumps(operation, ensure_ascii=False, separators=(",", ":"))
                    for operation in operations
                ),
            },
        )

    async def close(self) -> None:
        if self._review_task is None:
            return
        await self._review_queue.join()
        await self._review_queue.put(None)
        await self._review_task
        self._review_task = None

    async def _project_review(self) -> None:
        while True:
            event = await self._review_queue.get()
            try:
                if event is None:
                    return
                self._review_store.record(event)
            finally:
                self._review_queue.task_done()
