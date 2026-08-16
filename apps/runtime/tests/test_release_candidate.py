"""Structural checks for the Astera 1.0 release candidate."""
from __future__ import annotations

from pathlib import Path
import unittest


class ReleaseCandidateTests(unittest.TestCase):
    def test_release_candidate_is_immutable_and_gated(self) -> None:
        manifest = Path("infrastructure/release/astera-runtime-1.0.0-rc.1.yaml").read_text()
        workflow = Path(".github/workflows/release-candidate.yml").read_text()
        self.assertIn("version: 1.0.0-rc.1", manifest)
        self.assertIn("strategy: blue-green", manifest)
        self.assertIn("rollback: helm-revision", manifest)
        self.assertIn("needs: validate", workflow)
        self.assertIn("python -m pytest -q", workflow)
