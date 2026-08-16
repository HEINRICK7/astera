"""Unit tests for the Phase C kernel core without external services."""
from __future__ import annotations

import asyncio
import unittest
from typing import Awaitable, Callable

from apps.runtime.src.application.capabilities import CapabilityRegistry
from apps.runtime.src.application.context import ContextManager
from apps.runtime.src.application.kernel import AsteraKernel
from apps.runtime.src.domain.entities import CapabilityDescriptor
from apps.runtime.src.domain.value_objects import (
    CapabilityType,
    PluginName,
    PluginVersion,
    ProviderName,
    SelectionCriteria,
)


class FakeEventBus:
    """In-memory EventBusPort test double."""

    def __init__(self) -> None:
        self.connected = False
        self.published: list[tuple[str, bytes]] = []

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

    async def publish(self, subject: str, payload: bytes) -> None:
        self.published.append((subject, payload))

    async def subscribe(
        self,
        subject: str,
        handler: Callable[[bytes], Awaitable[None]],
    ) -> None:
        del subject, handler

    async def is_connected(self) -> bool:
        return self.connected


class KernelLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_kernel_boots_reports_health_and_stops(self) -> None:
        bus = FakeEventBus()
        kernel = AsteraKernel(bus)

        await kernel.startup()

        self.assertTrue(kernel.is_ready())
        self.assertTrue((await kernel.get_health())["event_bus"]["connected"])
        self.assertEqual(bus.published[0][0], "astera.kernel.ready")
        self.assertIs(kernel.orchestrator, kernel.orchestrator)

        await kernel.shutdown()

        self.assertFalse(kernel.is_ready())
        self.assertFalse(bus.connected)
        self.assertEqual(kernel.state.value, "stopped")


class ContextManagerTests(unittest.TestCase):
    def test_session_id_is_part_of_created_context(self) -> None:
        context = ContextManager().create_session("org-1", "workspace-1")

        self.assertEqual(context.session_id, context.id)
        self.assertEqual(context.organization_id, "org-1")
        self.assertFalse(context.is_clinical())


class CapabilityRegistryTests(unittest.TestCase):
    def test_select_best_prefers_language_and_streaming_match(self) -> None:
        registry = CapabilityRegistry()
        plugin = PluginName("speech-plugin")
        version = PluginVersion(1, 0, 0)

        registry.register(CapabilityDescriptor(
            capability_type=CapabilityType.SPEECH_TRANSCRIPTION,
            provider=ProviderName("batch-provider"),
            plugin=plugin,
            version=version,
            supported_languages=["en-US"],
            supports_streaming=False,
            accuracy_score=0.99,
        ))
        registry.register(CapabilityDescriptor(
            capability_type=CapabilityType.SPEECH_TRANSCRIPTION,
            provider=ProviderName("realtime-provider"),
            plugin=plugin,
            version=version,
            supported_languages=["pt-BR"],
            supports_streaming=True,
            avg_latency_ms=100,
            accuracy_score=0.92,
        ))

        selected = registry.select_best(
            CapabilityType.SPEECH_TRANSCRIPTION,
            SelectionCriteria(language="pt-BR", requires_streaming=True),
        )

        self.assertEqual(str(selected.provider), "realtime-provider")


if __name__ == "__main__":
    unittest.main()
