"""Kernel cleanup tests for failed plugin startup."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.kernel import AsteraKernel
from packages.plugin_sdk import PluginManifest
from apps.runtime.src.domain.value_objects import PluginName, PluginVersion


class FailingPlugin:
    plugin_name = PluginName("failing-plugin")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="test failure",
    )

    async def on_start(self) -> None:
        raise RuntimeError("startup failure")

    async def on_stop(self) -> None:
        return None

    async def invoke(self, provider, capability, payload, context):
        return {}


class FakeBus:
    def __init__(self) -> None:
        self.connected = False

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

    async def is_connected(self) -> bool:
        return self.connected

    async def publish(self, subject: str, payload: bytes) -> None:
        del subject, payload


class KernelFailureCleanupTests(unittest.IsolatedAsyncioTestCase):
    async def test_shutdown_disconnects_after_failed_startup(self) -> None:
        bus = FakeBus()
        kernel = AsteraKernel(bus)
        kernel.plugins.register(FailingPlugin())

        with self.assertRaises(RuntimeError):
            await kernel.startup()

        await kernel.shutdown()

        self.assertFalse(bus.connected)
        self.assertEqual(kernel.state.value, "stopped")
