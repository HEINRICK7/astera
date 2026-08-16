"""Tests for release rollback behavior and operational assets."""
from __future__ import annotations

from pathlib import Path
import unittest

from packages.release_sdk import InMemoryReleaseManager


class RollbackTests(unittest.TestCase):
    def test_rollback_restores_previous_image(self) -> None:
        releases = InMemoryReleaseManager()
        releases.deploy("sha-one")
        releases.deploy("sha-two")
        rollback = releases.rollback()
        self.assertEqual(rollback.status, "rolled_back")
        self.assertEqual(rollback.image_tag, "sha-one")
        self.assertEqual(rollback.previous_image_tag, "sha-two")

    def test_rollback_assets_require_explicit_revision(self) -> None:
        script = Path("infrastructure/scripts/rollback.sh").read_text()
        workflow = Path(".github/workflows/rollback.yml").read_text()
        self.assertIn('"${HELM_REVISION:?HELM_REVISION is required}"', script)
        self.assertIn("workflow_dispatch", workflow)
        self.assertIn("HELM_REVISION", workflow)
