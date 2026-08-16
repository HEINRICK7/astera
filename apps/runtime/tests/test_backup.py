"""Tests for backup manifests and checksum verification."""
from __future__ import annotations

import asyncio
import json
import unittest

from apps.runtime.src.adapters.http.backups import create_backup_router
from packages.auth_sdk import AuthService, LoginCredentials, Principal
from packages.backup_sdk import InMemoryBackupStore


class BackupTests(unittest.TestCase):
    def test_backup_round_trip_verifies_checksum(self) -> None:
        backups = InMemoryBackupStore()
        artifact = backups.create_backup("runtime-manifest", b"astera-state")
        self.assertEqual(artifact.size_bytes, 12)
        self.assertEqual(backups.restore(artifact.backup_id), b"astera-state")
        self.assertEqual(backups.list_backups()[0].backup_id, artifact.backup_id)

    def test_backup_manifest_route_is_rbac_protected(self) -> None:
        backups = InMemoryBackupStore()
        backups.create_backup("runtime-manifest", b"state")
        auth = AuthService(secret="x" * 48)
        credentials = LoginCredentials("backup@example.com", "password")
        auth.register_user(
            credentials,
            Principal(
                user_id="backup-1",
                email=credentials.email,
                organization_id="org-1",
                permissions=("backup:read",),
            ),
        )
        tokens = auth.login(credentials)
        router = create_backup_router(backups=backups, auth_service=auth)
        response = asyncio.run(
            router.routes[0].endpoint(principal=auth.authenticate(tokens.access_token))
        )
        self.assertEqual(len(json.loads(response.body)["data"]), 1)
