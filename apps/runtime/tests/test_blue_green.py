"""Structural checks for Blue/Green promotion assets."""
from __future__ import annotations

from pathlib import Path
import unittest


class BlueGreenTests(unittest.TestCase):
    def test_manifest_has_active_and_preview_services(self) -> None:
        manifest = Path("infrastructure/kubernetes/blue-green.yaml").read_text()
        self.assertIn("name: astera-runtime-blue", manifest)
        self.assertIn("name: astera-runtime-green", manifest)
        self.assertIn("name: astera-runtime-preview", manifest)
        self.assertIn("astera.io/color: blue", manifest)
        self.assertIn("astera.io/color: green", manifest)

    def test_promotion_validates_target_before_switching_service(self) -> None:
        script = Path("infrastructure/scripts/switch-color.sh").read_text()
        workflow = Path(".github/workflows/blue-green.yml").read_text()
        self.assertIn("blue|green", script)
        self.assertIn("rollout status", workflow)
        self.assertIn("Promote traffic", workflow)
