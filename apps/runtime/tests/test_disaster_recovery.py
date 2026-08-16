"""Tests for Disaster Recovery plans and readiness."""
from __future__ import annotations

import asyncio
import json
import unittest

from apps.runtime.src.adapters.http.disaster_recovery import create_recovery_router
from packages.auth_sdk import AuthService, LoginCredentials, Principal
from packages.disaster_recovery_sdk import InMemoryRecoveryCoordinator, RecoveryPlan


class DisasterRecoveryTests(unittest.TestCase):
    def test_drill_updates_plan_status(self) -> None:
        recovery = InMemoryRecoveryCoordinator()
        recovery.register(RecoveryPlan(service="runtime", rto_minutes=30, rpo_minutes=15))
        self.assertTrue(recovery.status().ready)
        recovery.record_drill("runtime", passed=False)
        self.assertFalse(recovery.status().ready)
        recovery.record_drill("runtime", passed=True)
        self.assertEqual(recovery.status().plans[0].status, "verified")

    def test_recovery_status_route_is_rbac_protected(self) -> None:
        recovery = InMemoryRecoveryCoordinator()
        recovery.register(RecoveryPlan(service="runtime", rto_minutes=30, rpo_minutes=15))
        auth = AuthService(secret="x" * 48)
        credentials = LoginCredentials("recovery@example.com", "password")
        auth.register_user(
            credentials,
            Principal(
                user_id="recovery-1",
                email=credentials.email,
                organization_id="org-1",
                permissions=("recovery:read",),
            ),
        )
        tokens = auth.login(credentials)
        router = create_recovery_router(recovery=recovery, auth_service=auth)
        response = asyncio.run(
            router.routes[0].endpoint(principal=auth.authenticate(tokens.access_token))
        )
        self.assertTrue(json.loads(response.body)["data"]["ready"])
