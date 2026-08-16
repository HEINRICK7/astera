"""Tests for runtime security posture and HTTP protection."""
from __future__ import annotations

import asyncio
import json
import unittest

from apps.runtime.src.adapters.http.security import create_security_router
from packages.auth_sdk import AuthService, LoginCredentials, Principal
from packages.security_sdk import SecurityPosture


class SecurityTests(unittest.TestCase):
    def test_production_baseline_rejects_development_controls(self) -> None:
        report = SecurityPosture().evaluate(
            environment="production",
            auth_secret="astera-development-secret-change-in-production",
            debug=True,
            docs_enabled=True,
        )
        self.assertFalse(report.passed)
        self.assertEqual(sum(check.status == "fail" for check in report.checks), 3)

    def test_security_report_route_is_rbac_protected(self) -> None:
        report = SecurityPosture().evaluate(
            environment="development",
            auth_secret="x" * 48,
            debug=False,
            docs_enabled=True,
        )
        auth = AuthService(secret="x" * 48)
        credentials = LoginCredentials("security@example.com", "password")
        auth.register_user(
            credentials,
            Principal(
                user_id="security-1",
                email=credentials.email,
                organization_id="org-1",
                permissions=("security:read",),
            ),
        )
        tokens = auth.login(credentials)
        router = create_security_router(report=report, auth_service=auth)
        response = asyncio.run(
            router.routes[0].endpoint(principal=auth.authenticate(tokens.access_token))
        )
        self.assertTrue(json.loads(response.body)["data"]["passed"])
