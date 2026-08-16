"""CPI-001 development bootstrap contract for an independent Workbench."""
from __future__ import annotations

import asyncio
import json
import unittest

from fastapi.security import HTTPAuthorizationCredentials

from apps.runtime.src.adapters.http.auth import LoginRequest, create_auth_router
from apps.runtime.src.adapters.http.patients import create_patient_router
from apps.runtime.src.adapters.http.workspaces import create_workspace_router
from apps.runtime.src.bootstrap.main import seed_development_workbench_fixture
from packages.auth_sdk import AuthService, AuthenticationError, LoginCredentials
from packages.patient_sdk import PatientDirectory
from packages.workspace_sdk import WorkspaceDirectory


class WorkbenchDevelopmentFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.auth = AuthService(secret="x" * 48)
        self.workspaces = WorkspaceDirectory()
        self.patients = PatientDirectory()

    def test_development_fixture_supports_login_workspace_and_patient_setup(self) -> None:
        seed_development_workbench_fixture(
            is_development=True,
            auth_service=self.auth,
            workspace_directory=self.workspaces,
            patient_directory=self.patients,
        )
        login_response = asyncio.run(
            create_auth_router(self.auth).routes[0].endpoint(
                LoginRequest(email="doctor@example.com", password="development-password")
            )
        )
        login_body = json.loads(login_response.body)
        token = login_body["data"]["access_token"]
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        workspace_response = asyncio.run(
            create_workspace_router(directory=self.workspaces, auth_service=self.auth)
            .routes[0]
            .endpoint(credentials)
        )
        patient_response = asyncio.run(
            create_patient_router(directory=self.patients, auth_service=self.auth)
            .routes[1]
            .endpoint(principal=self.auth.authenticate(token))
        )

        self.assertTrue(login_body["success"])
        self.assertEqual(
            json.loads(workspace_response.body)["data"],
            [{
                "workspace_id": "workspace-1",
                "organization_id": "org-1",
                "name": "Astera Development Workspace",
                "slug": "astera-development",
            }],
        )
        self.assertEqual(
            json.loads(patient_response.body)["data"],
            [{
                "patient_id": "patient-golden-consultation-001",
                "organization_id": "org-1",
                "full_name": "Golden Consultation 001",
                "birth_date": None,
                "active": True,
            }],
        )

    def test_fixture_is_not_registered_outside_development(self) -> None:
        seed_development_workbench_fixture(
            is_development=False,
            auth_service=self.auth,
            workspace_directory=self.workspaces,
            patient_directory=self.patients,
        )

        with self.assertRaises(AuthenticationError):
            self.auth.login(LoginCredentials("doctor@example.com", "development-password"))
        self.assertEqual(self.workspaces.get("workspace-1"), None)
