"""Integration tests for the first official Astera plugin."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities import CapabilityRegistry
from apps.runtime.src.application.orchestrator import TaskIntent, TaskOrchestrator
from apps.runtime.src.application.plugins.echo import EchoPlugin
from apps.runtime.src.application.providers import PluginResolver, ProviderRegistry
from apps.runtime.src.application.kernel import AsteraKernel
from apps.runtime.src.domain.entities import ContextScope
from apps.runtime.src.domain.value_objects import CapabilityType


class FakeEventBus:
    def __init__(self) -> None:
        self.connected = False

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

    async def is_connected(self) -> bool:
        return False

    async def publish(self, subject: str, payload: bytes) -> None:
        del subject, payload


class EchoPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_capability_provider_resolver_plugin_chain(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = EchoPlugin(capabilities, providers, resolver)

        await plugin.on_start()
        orchestrator = TaskOrchestrator(
            capabilities=capabilities,
            providers=providers,
            resolver=resolver,
            event_bus=FakeEventBus(),
        )
        result = await orchestrator.execute(TaskIntent(
            capability_type=CapabilityType.PLATFORM_ECHO,
            payload={"message": "hello"},
            context=ContextScope(organization_id="system"),
        ))

        self.assertTrue(result.success)
        self.assertEqual(result.provider_name, "echo")
        self.assertEqual(result.output["payload"], {"message": "hello"})

        await plugin.on_stop()
        self.assertFalse(capabilities.has_capability(CapabilityType.PLATFORM_ECHO))

    async def test_kernel_bootstrap_starts_echo_and_executes_api_port(self) -> None:
        bus = FakeEventBus()
        kernel = AsteraKernel(bus)
        kernel.plugins.register(EchoPlugin(
            capabilities=kernel.capabilities,
            providers=kernel.providers,
            resolver=kernel.resolver,
        ))

        await kernel.startup()
        result = await kernel.execute_task(TaskIntent(
            capability_type=CapabilityType.PLATFORM_ECHO,
            payload="booted",
            context=ContextScope(organization_id="system"),
        ))

        self.assertTrue(result.success)
        self.assertEqual(kernel.plugins.summary()["started"], 1)
        await kernel.shutdown()
        self.assertFalse(bus.connected)
