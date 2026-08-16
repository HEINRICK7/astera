"""Structural checks for the first Kubernetes production manifest."""
from __future__ import annotations

from pathlib import Path
import unittest


class KubernetesManifestTests(unittest.TestCase):
    def test_runtime_manifest_has_safe_rollout_and_probes(self) -> None:
        manifest = Path("infrastructure/kubernetes/astera-runtime.yaml").read_text()
        for required in (
            "kind: Deployment",
            "replicas: 2",
            "type: RollingUpdate",
            "maxUnavailable: 0",
            "maxSurge: 1",
            "path: /ready",
            "path: /health",
            "runAsNonRoot: true",
            "kind: Service",
            "kind: PodDisruptionBudget",
        ):
            self.assertIn(required, manifest)
