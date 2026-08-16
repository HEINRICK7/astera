"""Tests for tenant-scoped audit records and protected reads."""
from __future__ import annotations

import asyncio
import json
import unittest

from apps.runtime.src.adapters.http.audit import create_audit_router
from packages.audit_sdk import AuditEntry, InMemoryAuditLog
from packages.auth_sdk import AuthService, LoginCredentials, Principal


class AuditTests(unittest.TestCase):
    def test_records_are_redacted_and_reads_are_tenant_scoped(self) -> None:
        audit = InMemoryAuditLog(max_entries=2)
        audit.append(
            AuditEntry.create(
                organization_id="org-1",
                actor_id="user-1",
                action="patient.read",
                resource_type="patient",
                resource_id="patient-1",
                metadata={"password": "do-not-store", "source": "api"},
            )
        )
        audit.append(
            AuditEntry.create(
                organization_id="org-2",
                actor_id="user-2",
                action="patient.read",
                resource_type="patient",
            )
        )

        org_one = audit.list_for_organization("org-1")
        self.assertEqual(len(org_one), 1)
        self.assertEqual(dict(org_one[0].metadata)["password"], "[REDACTED]")
        self.assertEqual(audit.list_for_organization("org-2")[0].organization_id, "org-2")

    def test_http_read_requires_audit_permission_and_uses_principal_tenant(self) -> None:
        audit = InMemoryAuditLog()
        audit.append(
            AuditEntry.create(
                organization_id="org-1",
                actor_id="system",
                action="runtime.bootstrap",
                resource_type="runtime",
            )
        )
        auth = AuthService(secret="x" * 48)
        credentials = LoginCredentials("auditor@example.com", "password")
        principal = Principal(
            user_id="auditor-1",
            email=credentials.email,
            organization_id="org-1",
            permissions=("audit:read",),
        )
        auth.register_user(credentials, principal)
        tokens = auth.login(credentials)
        router = create_audit_router(audit_log=audit, auth_service=auth)

        response = asyncio.run(
            router.routes[0].endpoint(
                principal=auth.authenticate(tokens.access_token),
                action=None,
                limit=100,
            )
        )
        body = json.loads(response.body)
        self.assertEqual(len(body["data"]), 1)
        self.assertEqual(body["data"][0]["organization_id"], "org-1")
