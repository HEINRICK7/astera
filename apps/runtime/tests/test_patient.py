"""Tests for organization-isolated patient records."""
from __future__ import annotations

import unittest

from packages.auth_sdk import Principal
from packages.patient_sdk import PatientDirectory


class PatientTests(unittest.TestCase):
    def test_patient_directory_isolated_by_organization(self) -> None:
        directory = PatientDirectory()
        org_one = Principal("user-1", "one@example.com", "org-1")
        org_two = Principal("user-2", "two@example.com", "org-2")
        patient = directory.create(org_one, full_name="Ana Silva")

        self.assertEqual(directory.get(org_one, patient.patient_id).full_name, "Ana Silva")
        self.assertIsNone(directory.get(org_two, patient.patient_id))
        self.assertEqual(directory.list_for(org_one), (patient,))
        self.assertEqual(directory.list_for(org_two), ())
