"""Structural checks for the production Helm chart."""
from __future__ import annotations

from pathlib import Path
import unittest


class HelmChartTests(unittest.TestCase):
    root = Path("infrastructure/helm/astera")

    def test_chart_is_parameterized_and_uses_external_secret(self) -> None:
        chart = (self.root / "Chart.yaml").read_text()
        values = (self.root / "values.yaml").read_text()
        deployment = (self.root / "templates/deployment.yaml").read_text()
        self.assertIn("apiVersion: v2", chart)
        self.assertIn("replicaCount: 2", values)
        self.assertIn("{{ .Values.image.repository }}", deployment)
        self.assertIn("secretKeyRef:", deployment)
        self.assertIn("{{ .Values.authSecretName }}", deployment)
        self.assertIn("maxUnavailable: 0", deployment)
