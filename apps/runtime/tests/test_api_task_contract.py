"""Tests for the official task API boundary."""
from __future__ import annotations

import unittest
import json

from apps.runtime.src.adapters.http.tasks import ExecuteTaskRequest, create_task_router
from apps.runtime.src.adapters.http.plugins import create_plugin_router
from apps.runtime.src.application.orchestrator.task_result import TaskResult
from apps.runtime.src.application.kernel import AsteraKernel
from apps.runtime.src.adapters.nats import NatsEventBusAdapter
from apps.runtime.src.domain.value_objects import CapabilityType


class ApiTaskContractTests(unittest.TestCase):
    def test_task_request_defaults_to_phase_c_echo(self) -> None:
        request = ExecuteTaskRequest(payload={"message": "hello"})

        self.assertEqual(request.capability_type.value, "platform.echo")
        self.assertEqual(request.organization_id, "system")

    def test_router_is_versioned_and_has_task_endpoint(self) -> None:
        kernel = AsteraKernel(NatsEventBusAdapter("nats://localhost:4222"))
        router = create_task_router(kernel)

        self.assertEqual(router.prefix, "/api/v1")
        self.assertEqual(router.routes[0].path, "/api/v1/tasks")

    def test_success_response_uses_official_envelope(self) -> None:
        class FakeKernel:
            async def execute_task(self, intent):
                return TaskResult(
                    request_id=intent.request_id,
                    capability_type=CapabilityType.PLATFORM_ECHO,
                    success=True,
                    output={"echo": intent.payload},
                )

        router = create_task_router(FakeKernel())
        endpoint = router.routes[0].endpoint
        response = __import__("asyncio").run(endpoint(
            ExecuteTaskRequest(payload={"message": "hello"})
        ))
        body = json.loads(response.body)

        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["output"], {"echo": {"message": "hello"}})
        self.assertIn("trace_id", body)

    def test_plugin_routes_are_versioned(self) -> None:
        class FakeRegistry:
            async def list_plugins(self):
                return []

            async def get_plugin(self, plugin_name):
                return {"plugin": plugin_name}

        router = create_plugin_router(FakeRegistry())
        self.assertEqual(
            [route.path for route in router.routes],
            ["/api/v1/plugins", "/api/v1/plugins/{plugin_name}"],
        )
