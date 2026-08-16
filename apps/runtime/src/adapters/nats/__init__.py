"""
Astera Runtime — NATS Event Bus Adapter (Outbound Adapter).

Implements the EventBusPort interface using NATS as the message broker.
This is the only place in the Runtime that imports the nats-py library.

The application layer NEVER imports this adapter directly.
It receives it via Dependency Injection through the EventBusPort interface.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Callable, Awaitable

from apps.runtime.src.ports.outbound import EventBusPort
from apps.runtime.src.domain.exceptions import EventBusError, EventBusNotConnectedError

logger = logging.getLogger("astera.runtime.adapters.nats")


class NatsEventBusAdapter(EventBusPort):
    """
    NATS implementation of the EventBusPort.

    Wraps nats-py with Astera-specific error handling,
    reconnection logic, and structured logging.
    """

    def __init__(
        self,
        nats_url: str,
        connect_timeout: float = 5.0,
        reconnect_time_wait: float = 2.0,
        max_reconnect_attempts: int = 10,
        startup_retries: int = 3,
    ) -> None:
        self._nats_url = nats_url
        self._connect_timeout = connect_timeout
        self._reconnect_time_wait = reconnect_time_wait
        self._max_reconnect_attempts = max_reconnect_attempts
        self._startup_retries = max(1, startup_retries)
        self._client = None  # nats.aio.client.Client — imported lazily

    async def connect(self) -> None:
        """Establish connection to NATS."""
        if await self.is_connected():
            return
        import nats

        last_error: Exception | None = None
        for attempt in range(1, self._startup_retries + 1):
            try:
                self._client = await nats.connect(
                    servers=[self._nats_url],
                    connect_timeout=self._connect_timeout,
                    reconnect_time_wait=self._reconnect_time_wait,
                    max_reconnect_attempts=self._max_reconnect_attempts,
                    error_cb=self._on_error,
                    disconnected_cb=self._on_disconnect,
                    reconnected_cb=self._on_reconnect,
                )
                logger.info(
                    "Connected to NATS",
                    extra={"url": self._nats_url, "attempt": attempt},
                )
                return
            except Exception as exc:
                last_error = exc
                self._client = None
                logger.warning(
                    "NATS connection attempt failed",
                    extra={"url": self._nats_url, "attempt": attempt, "error": str(exc)},
                )
                if attempt < self._startup_retries:
                    await asyncio.sleep(min(2.0, 0.25 * (2 ** (attempt - 1))))
        assert last_error is not None
        logger.error("Failed to connect to NATS", extra={"url": self._nats_url, "error": str(last_error)})
        raise EventBusError(f"NATS connection failed: {last_error}") from last_error

    async def disconnect(self) -> None:
        """Gracefully drain and close NATS connection."""
        if self._client and not self._client.is_closed:
            try:
                await self._client.drain()
                logger.info("NATS connection drained and closed")
            except Exception as exc:
                logger.warning("Error during NATS drain", extra={"error": str(exc)})
            finally:
                self._client = None

    async def publish(self, subject: str, payload: bytes) -> None:
        """Publish a message to a NATS subject."""
        if not await self.is_connected():
            raise EventBusNotConnectedError()
        try:
            await self._client.publish(subject, payload)
            logger.debug("Published to NATS", extra={"subject": subject, "bytes": len(payload)})
        except Exception as exc:
            raise EventBusError(f"Failed to publish to '{subject}': {exc}") from exc

    async def subscribe(
        self,
        subject: str,
        handler: Callable[[bytes], Awaitable[None]],
    ) -> None:
        """Subscribe to a NATS subject with an async handler."""
        if not await self.is_connected():
            raise EventBusNotConnectedError()

        async def _wrapper(msg):
            try:
                await handler(msg.data)
            except Exception as exc:
                logger.error(
                    "Error in NATS message handler",
                    extra={"subject": subject, "error": str(exc)},
                    exc_info=True,
                )

        await self._client.subscribe(subject, cb=_wrapper)
        logger.info("Subscribed to NATS subject", extra={"subject": subject})

    async def is_connected(self) -> bool:
        """Return True if the NATS client is connected and not closed."""
        return self._client is not None and not self._client.is_closed

    async def health_check(self) -> None:
        if not await self.is_connected():
            raise EventBusNotConnectedError()

    # ── NATS Callbacks ────────────────────────────────────────────────────────

    async def _on_error(self, exc: Exception) -> None:
        logger.error("NATS error", extra={"error": str(exc)}, exc_info=True)

    async def _on_disconnect(self) -> None:
        logger.warning("NATS disconnected")

    async def _on_reconnect(self) -> None:
        logger.info("NATS reconnected")
