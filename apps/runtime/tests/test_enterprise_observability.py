"""Tests for enterprise operational observability."""
from __future__ import annotations

import asyncio
import json
import unittest

from apps.runtime.src.adapters.http.observability import create_observability_router
from packages.auth_sdk import AuthService, LoginCredentials, Principal
from packages.observability_sdk import InMemoryOperationalObservability


class EnterpriseObservabilityTests(unittest.TestCase):
    def test_metrics_accumulate_and_events_are_bounded(self) -> None:
        telemetry = InMemoryOperationalObservability(max_events=2)
        telemetry.increment_counter("runtime.tasks", attributes={"status": "success"})
        telemetry.increment_counter("runtime.tasks", 2, {"status": "success"})
        telemetry.set_gauge("runtime.active_workers", 3)
        telemetry.record_event("runtime.started")
        telemetry.record_event("runtime.ready")
        telemetry.record_event("runtime.request", severity="warning")

        snapshot = telemetry.snapshot()
        self.assertEqual(len(snapshot.metrics), 2)
        self.assertEqual(snapshot.metrics[0].name, "runtime.active_workers")
        self.assertEqual(snapshot.metrics[1].value, 3)
        self.assertEqual(len(snapshot.events), 2)
        self.assertEqual(snapshot.events[0].name, "runtime.ready")

    def test_http_snapshot_requires_observability_permission(self) -> None:
        telemetry = InMemoryOperationalObservability()
        telemetry.record_event("runtime.ready", attributes={"environment": "test"})
        auth = AuthService(secret="x" * 48)
        credentials = LoginCredentials("operator@example.com", "password")
        auth.register_user(
            credentials,
            Principal(
                user_id="operator-1",
                email=credentials.email,
                organization_id="org-1",
                permissions=("observability:read",),
            ),
        )
        tokens = auth.login(credentials)
        router = create_observability_router(observability=telemetry, auth_service=auth)

        response = asyncio.run(router.routes[0].endpoint(principal=auth.authenticate(tokens.access_token)))
        body = json.loads(response.body)
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["events"][0]["name"], "runtime.ready")
