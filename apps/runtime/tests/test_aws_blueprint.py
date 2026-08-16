"""Structural checks for the AWS production blueprint."""
from __future__ import annotations

from pathlib import Path
import unittest


class AwsBlueprintTests(unittest.TestCase):
    root = Path("infrastructure/aws")

    def test_eks_blueprint_uses_external_network_and_iam_inputs(self) -> None:
        main = (self.root / "main.tf").read_text()
        variables = (self.root / "variables.tf").read_text()
        example = (self.root / "terraform.tfvars.example").read_text()
        self.assertIn('source  = "hashicorp/aws"', (self.root / "versions.tf").read_text())
        self.assertIn("aws_eks_cluster", main)
        self.assertIn("endpoint_public_access  = false", main)
        self.assertIn("private_subnet_ids", variables)
        self.assertIn("cluster_role_arn", variables)
        self.assertIn("REPLACE_ME", example)
        self.assertNotIn("aws_access_key", main + variables + example)
