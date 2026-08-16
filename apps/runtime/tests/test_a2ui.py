"""Tests for renderer-neutral A2UI workspace documents."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.a2ui import A2UIService
from apps.runtime.src.application.dashboard import DashboardService
from packages.a2ui_sdk import A2UIDocument
from packages.auth_sdk import Principal
from packages.encounter_sdk import EncounterDirectory
from packages.patient_sdk import PatientDirectory
from packages.timeline_sdk import TimelineDirectory


class A2UITests(unittest.TestCase):
    def test_workspace_view_has_root_and_metrics_nodes(self) -> None:
        principal = Principal("user-1", "doctor@example.com", "org-1", ("workspace-1",))
        dashboard = DashboardService(
            patients=PatientDirectory(),
            encounters=EncounterDirectory(),
            timeline=TimelineDirectory(),
        )
        document = A2UIService(dashboard).workspace_view(principal)

        self.assertIsInstance(document, A2UIDocument)
        self.assertEqual(document.root_id, "workspace-root")
        self.assertEqual({node.component for node in document.nodes}, {"ClinicalWorkspace", "WorkspaceHeader", "MetricGrid"})

    def test_consultation_view_contains_clinical_workspace_panels(self) -> None:
        principal = Principal("user-1", "doctor@example.com", "org-1", ("workspace-1",))
        patients = PatientDirectory()
        encounters = EncounterDirectory()
        timeline = TimelineDirectory()
        patient = patients.create(principal, full_name="Ana Silva")
        encounter = encounters.create(principal, workspace_id="workspace-1", patient_id=patient.patient_id)
        timeline.append(principal, patient_id=patient.patient_id, event_type="encounter.created")
        dashboard = DashboardService(
            patients=patients,
            encounters=encounters,
            timeline=timeline,
        )

        document = A2UIService(dashboard).consultation_view(
            patient=patient,
            encounter=encounter,
            timeline=timeline.list_for(principal, patient.patient_id),
        )

        self.assertEqual(document.view_id, "clinical-consultation")
        self.assertEqual(len(document.nodes[0].children), 5)
        self.assertIn("AudioStream", {node.component for node in document.nodes})
        self.assertIn("RepresentationPanel", {node.component for node in document.nodes})
