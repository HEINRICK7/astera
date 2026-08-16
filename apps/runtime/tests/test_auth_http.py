"""Tests for versioned authentication routes."""
from __future__ import annotations

import asyncio
import json
import unittest

from apps.runtime.src.adapters.http.auth import LoginRequest, RefreshRequest, create_auth_router
from packages.auth_sdk import AuthService, LoginCredentials, Principal


class AuthHttpTests(unittest.TestCase):
    def test_login_and_refresh_use_versioned_contract(self) -> None:
        service = AuthService(secret="x" * 48)
        credentials = LoginCredentials("doctor@example.com", "password")
        service.register_user(
            credentials,
            Principal(
                user_id="professional-1",
                email=credentials.email,
                organization_id="org-1",
            ),
        )
        router = create_auth_router(service)

        self.assertEqual(router.prefix, "/api/v1/auth")
        login_response = asyncio.run(router.routes[0].endpoint(LoginRequest(email=credentials.email, password="password")))
        login_body = json.loads(login_response.body)
        self.assertTrue(login_body["success"])
        self.assertIn("refresh_token", login_body["data"])

        refresh_response = asyncio.run(
            router.routes[1].endpoint(RefreshRequest(refresh_token=login_body["data"]["refresh_token"]))
        )
        self.assertTrue(json.loads(refresh_response.body)["success"])
