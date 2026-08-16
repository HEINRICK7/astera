"""Tests for the LGPD privacy workflow."""
from __future__ import annotations

import asyncio
import json
import unittest

from apps.runtime.src.adapters.http.privacy import ConsentRequest, create_privacy_router
from packages.auth_sdk import AuthService, LoginCredentials, Principal
from packages.privacy_sdk import ConsentRecord, DataSubjectRequest, InMemoryPrivacyService


class PrivacyTests(unittest.TestCase):
    def test_consent_and_requests_are_scoped_to_organization(self) -> None:
        privacy = InMemoryPrivacyService()
        privacy.record_consent(
            ConsentRecord.create(
                organization_id="org-1",
                subject_id="patient-1",
                purpose="clinical-care",
                policy_version="2026-01",
                granted=True,
            )
        )
        privacy.request(DataSubjectRequest.create(organization_id="org-1", subject_id="patient-1", request_type="access"))
        self.assertEqual(len(privacy.list_consents("org-1", "patient-1")), 1)
        self.assertEqual(len(privacy.list_consents("org-2", "patient-1")), 0)
        self.assertEqual(privacy.list_requests("org-1")[0].request_type, "access")

    def test_consent_route_uses_principal_organization(self) -> None:
        privacy = InMemoryPrivacyService()
        auth = AuthService(secret="x" * 48)
        credentials = LoginCredentials("privacy@example.com", "password")
        principal = Principal(
            user_id="privacy-1",
            email=credentials.email,
            organization_id="org-1",
            permissions=("privacy:write",),
        )
        auth.register_user(credentials, principal)
        tokens = auth.login(credentials)
        router = create_privacy_router(privacy=privacy, auth_service=auth)
        response = asyncio.run(
            router.routes[0].endpoint(
                ConsentRequest(
                    subject_id="patient-1",
                    purpose="clinical-care",
                    policy_version="2026-01",
                    granted=True,
                ),
                principal=auth.authenticate(tokens.access_token),
            )
        )
        body = json.loads(response.body)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(body["data"]["organization_id"], "org-1")
