"""Tests for tenant-safe encounter lifecycle."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.context.manager import ContextManager
from packages.auth_sdk import Principal
from packages.encounter_sdk import EncounterDirectory


class EncounterTests(unittest.TestCase):
    def test_encounter_lifecycle_is_bound_to_professional_workspace(self) -> None:
        principal = Principal(
            user_id="professional-1",
            email="doctor@example.com",
            organization_id="org-1",
            workspace_ids=("workspace-1",),
        )
        directory = EncounterDirectory()
        encounter = directory.create(principal, workspace_id="workspace-1", patient_id="patient-1")

        started = directory.start(principal, encounter.encounter_id)
        completed = directory.complete(principal, encounter.encounter_id)

        self.assertEqual(started.status, "in_progress")
        self.assertEqual(completed.status, "completed")
        self.assertIsNotNone(completed.started_at)
        self.assertIsNotNone(completed.ended_at)

    def test_context_manager_can_attach_encounter_to_runtime_session(self) -> None:
        context_manager = ContextManager()
        context = context_manager.create_session("org-1", "workspace-1")

        attached = context_manager.start_encounter(
            context.session_id,
            "encounter-1",
            "patient-1",
        )

        self.assertEqual(attached.encounter_id, "encounter-1")
        self.assertEqual(attached.patient_id, "patient-1")

    def test_patient_journey_updates_shared_encounter_status(self) -> None:
        principal = Principal(
            user_id="professional-1",
            email="doctor@example.com",
            organization_id="org-1",
            workspace_ids=("workspace-1",),
        )
        directory = EncounterDirectory()
        encounter = directory.create(principal, workspace_id="workspace-1", patient_id="patient-1")

        joined = directory.patient_join(encounter.encounter_id)
        consented = directory.patient_consent(encounter.encounter_id, accepted=True)
        ready = directory.patient_equipment(
            encounter.encounter_id,
            camera_ready=True,
            microphone_ready=True,
        )

        self.assertIsNotNone(joined.patient_joined_at)
        self.assertEqual(consented.consent_status, "accepted")
        self.assertTrue(ready.camera_ready)
        self.assertTrue(ready.microphone_ready)
        self.assertEqual(directory.get_public(encounter.encounter_id), ready)
