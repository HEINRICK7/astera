"""Tests for ordered asynchronous streaming."""
from __future__ import annotations

import asyncio
import unittest

from packages.streaming_sdk import InMemoryStreamBroker, StreamEvent


class StreamingTests(unittest.IsolatedAsyncioTestCase):
    async def test_subscriber_receives_ordered_events(self) -> None:
        broker = InMemoryStreamBroker()
        received = []

        async def consume() -> None:
            async for event in broker.subscribe("stream-1"):
                received.append(event)
                if len(received) == 2:
                    break

        consumer = asyncio.create_task(consume())
        await asyncio.sleep(0)
        await broker.publish(StreamEvent("stream-1", "transcript.delta", 0, {"text": "Olá"}))
        await broker.publish(StreamEvent("stream-1", "transcript.completed", 1, {"text": "Olá."}))
        await asyncio.wait_for(consumer, timeout=1)

        self.assertEqual([event.sequence for event in received], [0, 1])
        self.assertEqual(received[1].event_type, "transcript.completed")
