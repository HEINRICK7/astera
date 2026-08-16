"""Tests for tenant-scoped dashboard aggregation."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.dashboard import DashboardService
from packages.auth_sdk import Principal
from packages.encounter_sdk import EncounterDirectory
from packages.patient_sdk import PatientDirectory
from packages.timeline_sdk import TimelineDirectory


class DashboardTests(unittest.TestCase):
    def test_dashboard_aggregates_only_the_principal_scope(self) -> None:
        principal = Principal(
            "user-1",
            "doctor@example.com",
            "org-1",
            workspace_ids=("workspace-1",),
        )
        patients = PatientDirectory()
        encounters = EncounterDirectory()
        timeline = TimelineDirectory()
        patient = patients.create(principal, full_name="Ana Silva")
        encounter = encounters.create(principal, workspace_id="workspace-1", patient_id=patient.patient_id)
        encounters.start(principal, encounter.encounter_id)
        timeline.append(principal, patient_id=patient.patient_id, event_type="encounter.started")

        snapshot = DashboardService(
            patients=patients,
            encounters=encounters,
            timeline=timeline,
        ).snapshot(principal)

        self.assertEqual(snapshot.patient_count, 1)
        self.assertEqual(snapshot.encounter_count, 1)
        self.assertEqual(snapshot.active_encounter_count, 1)
        self.assertEqual(snapshot.timeline_event_count, 1)
