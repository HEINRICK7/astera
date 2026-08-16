"""Tests for tenant-safe workspace listing."""
from __future__ import annotations

import asyncio
import json
import unittest

from fastapi.security import HTTPAuthorizationCredentials

from apps.runtime.src.adapters.http.workspaces import create_workspace_router
from packages.auth_sdk import AuthService, LoginCredentials, Principal
from packages.workspace_sdk import Workspace, WorkspaceDirectory


class WorkspaceTests(unittest.TestCase):
    def test_authenticated_principal_sees_only_memberships_in_organization(self) -> None:
        auth = AuthService(secret="x" * 48)
        credentials = LoginCredentials("doctor@example.com", "password")
        auth.register_user(
            credentials,
            Principal(
                user_id="professional-1",
                email=credentials.email,
                organization_id="org-1",
                workspace_ids=("workspace-1",),
            ),
        )
        tokens = auth.login(credentials)
        directory = WorkspaceDirectory()
        directory.register(Workspace("workspace-1", "org-1", "Clinic", "clinic"))
        directory.register(Workspace("workspace-2", "org-1", "Other", "other"))
        directory.register(Workspace("workspace-3", "org-2", "Foreign", "foreign"))
        router = create_workspace_router(directory=directory, auth_service=auth)

        response = asyncio.run(
            router.routes[0].endpoint(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials=tokens.access_token)
            )
        )
        body = json.loads(response.body)

        self.assertTrue(body["success"])
        self.assertEqual([item["workspace_id"] for item in body["data"]], ["workspace-1"])
