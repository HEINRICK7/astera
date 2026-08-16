"""Structural checks for the first production deploy runbook."""
from __future__ import annotations

from pathlib import Path
import unittest


class FirstDeployTests(unittest.TestCase):
    def test_deploy_is_atomic_and_waits_for_rollout(self) -> None:
        script = Path("infrastructure/scripts/first-deploy.sh").read_text()
        workflow = Path(".github/workflows/first-deploy.yml").read_text()
        self.assertIn("--atomic", script)
        self.assertIn("--wait", script)
        self.assertIn("rollout status", script)
        self.assertIn("workflow_dispatch", workflow)
        self.assertIn("image_tag", workflow)
