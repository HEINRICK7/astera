"""Tests for Plugin SDK registration and lifecycle."""
from __future__ import annotations

import unittest
from typing import Any

from apps.runtime.src.domain.value_objects import (
    CapabilityType,
    PluginName,
    PluginVersion,
    ProviderName,
)
from packages.plugin_sdk import PluginLifecycleError, PluginManifest, PluginRegistry


class FakePlugin:
    plugin_name = PluginName("echo-plugin")
    manifest = PluginManifest(
        name=plugin_name,
        version=PluginVersion(1, 0, 0),
        description="test plugin",
    )

    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    async def on_start(self) -> None:
        self.started = True

    async def on_stop(self) -> None:
        self.stopped = True

    async def invoke(
        self,
        provider: ProviderName,
        capability: CapabilityType,
        payload: Any,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "provider": str(provider),
            "capability": capability.value,
            "payload": payload,
            "context": context,
        }


class PluginRegistryTests(unittest.IsolatedAsyncioTestCase):
    async def test_plugin_lifecycle_and_summary(self) -> None:
        plugin = FakePlugin()
        registry = PluginRegistry()
        registry.register(plugin)

        await registry.start_all()
        await registry.stop_all()

        self.assertTrue(plugin.started)
        self.assertTrue(plugin.stopped)
        self.assertEqual(registry.summary()["plugins"][0]["state"], "stopped")

    def test_duplicate_registration_is_rejected(self) -> None:
        registry = PluginRegistry()
        registry.register(FakePlugin())

        with self.assertRaises(PluginLifecycleError):
            registry.register(FakePlugin())

    def test_discovery_and_health_expose_manifest(self) -> None:
        registry = PluginRegistry()
        self.assertEqual(registry.discover([FakePlugin()]), ["echo-plugin"])

        summary = registry.summary()["plugins"][0]
        self.assertEqual(summary["manifest"]["version"], "1.0.0")
        self.assertFalse(registry.health()[0]["healthy"])
