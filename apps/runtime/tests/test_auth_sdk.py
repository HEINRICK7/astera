"""Tests for authentication, JWT claims, refresh rotation, and RBAC."""
from __future__ import annotations

import unittest

from packages.auth_sdk import (
    AuthService,
    AuthenticationError,
    AuthorizationError,
    LoginCredentials,
    Principal,
)


class AuthSdkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AuthService(secret="x" * 48)
        self.principal = Principal(
            user_id="professional-1",
            email="doctor@example.com",
            organization_id="org-1",
            workspace_ids=("workspace-1",),
            roles=("professional",),
            permissions=("encounter:read", "encounter:write"),
        )
        self.credentials = LoginCredentials("doctor@example.com", "correct-password")
        self.service.register_user(self.credentials, self.principal)

    def test_login_authenticates_claims_and_rbac(self) -> None:
        tokens = self.service.login(self.credentials)
        authenticated = self.service.authenticate(tokens.access_token)

        self.assertEqual(authenticated.user_id, "professional-1")
        self.assertEqual(authenticated.organization_id, "org-1")
        self.service.require_permission(authenticated, "encounter:write")
        with self.assertRaises(AuthorizationError):
            self.service.require_permission(authenticated, "patient:delete")

    def test_refresh_rotates_and_invalidates_previous_token(self) -> None:
        tokens = self.service.login(self.credentials)
        refreshed = self.service.refresh(tokens.refresh_token)

        self.assertNotEqual(tokens.refresh_token, refreshed.refresh_token)
        with self.assertRaises(AuthenticationError):
            self.service.refresh(tokens.refresh_token)

    def test_invalid_credentials_are_rejected(self) -> None:
        with self.assertRaises(AuthenticationError):
            self.service.login(LoginCredentials("doctor@example.com", "wrong-password"))
