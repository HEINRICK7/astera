"""Structural checks for the production delivery assets."""
from __future__ import annotations

from pathlib import Path
import unittest


class DeliveryAssetsTests(unittest.TestCase):
    def test_container_runs_as_non_root_and_exposes_healthcheck(self) -> None:
        dockerfile = Path("Dockerfile").read_text()
        self.assertIn("USER astera", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)
        self.assertIn("uvicorn", dockerfile)

    def test_delivery_workflow_gates_image_and_chart_on_validation(self) -> None:
        workflow = Path(".github/workflows/production.yml").read_text()
        self.assertIn("needs: validate", workflow)
        self.assertIn("docker/build-push-action", workflow)
        self.assertIn("helm lint infrastructure/helm/astera", workflow)
