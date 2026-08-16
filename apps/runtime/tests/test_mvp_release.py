"""Structural checks for the stable Astera MVP 1.0 release."""
from __future__ import annotations

from pathlib import Path
import unittest


class MvpReleaseTests(unittest.TestCase):
    def test_stable_release_carries_the_validated_clinical_flow(self) -> None:
        manifest = Path("infrastructure/release/astera-runtime-1.0.0.yaml").read_text()
        workflow = Path(".github/workflows/mvp-1.0.yml").read_text()
        for stage in ("login", "patient", "encounter", "speech", "evidence", "knowledge", "soap", "save"):
            self.assertIn(f"{stage}: validated", manifest)
        self.assertIn("version: 1.0.0", manifest)
        self.assertIn("ASTERA_IMAGE_TAG: 1.0.0", workflow)
        self.assertIn("first-deploy.sh", workflow)
