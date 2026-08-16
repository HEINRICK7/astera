"""Tests for latency summaries and performance route."""
from __future__ import annotations

import asyncio
import json
import unittest

from apps.runtime.src.adapters.http.performance import create_performance_router
from packages.auth_sdk import AuthService, LoginCredentials, Principal
from packages.performance_sdk import InMemoryPerformanceMonitor


class PerformanceTests(unittest.TestCase):
    def test_latency_percentiles_and_error_rate_are_reported(self) -> None:
        monitor = InMemoryPerformanceMonitor()
        for duration in (10, 20, 30, 40, 100):
            monitor.record("http.request", duration, success=duration != 100)
        result = monitor.snapshot().operations[0]
        self.assertEqual(result.sample_count, 5)
        self.assertEqual(result.error_count, 1)
        self.assertEqual(result.p50_ms, 30)
        self.assertEqual(result.p95_ms, 100)

    def test_performance_route_is_rbac_protected(self) -> None:
        monitor = InMemoryPerformanceMonitor()
        monitor.record("http.request", 12)
        auth = AuthService(secret="x" * 48)
        credentials = LoginCredentials("performance@example.com", "password")
        auth.register_user(
            credentials,
            Principal(
                user_id="performance-1",
                email=credentials.email,
                organization_id="org-1",
                permissions=("performance:read",),
            ),
        )
        tokens = auth.login(credentials)
        router = create_performance_router(performance=monitor, auth_service=auth)
        response = asyncio.run(
            router.routes[0].endpoint(principal=auth.authenticate(tokens.access_token))
        )
        self.assertEqual(json.loads(response.body)["data"]["operations"][0]["sample_count"], 1)
