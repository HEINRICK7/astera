"""Tenant-scoped dashboard aggregation."""
from __future__ import annotations

from packages.auth_sdk import Principal
from packages.dashboard_sdk import DashboardSnapshot
from apps.runtime.src.ports.outbound.persistence import (
    EncounterRepositoryPort,
    PatientRepositoryPort,
    TimelineRepositoryPort,
)


class DashboardService:
    """Aggregate existing bounded directories without owning their data."""

    def __init__(
        self,
        *,
        patients: PatientRepositoryPort,
        encounters: EncounterRepositoryPort,
        timeline: TimelineRepositoryPort,
    ) -> None:
        self._patients = patients
        self._encounters = encounters
        self._timeline = timeline

    def snapshot(self, principal: Principal) -> DashboardSnapshot:
        encounters = self._encounters.list_for(principal)
        events = tuple(
            event
            for patient in self._patients.list_for(principal)
            for event in self._timeline.list_for(principal, patient.patient_id)
        )
        return DashboardSnapshot(
            organization_id=principal.organization_id,
            workspace_ids=principal.workspace_ids,
            patient_count=len(self._patients.list_for(principal)),
            encounter_count=len(encounters),
            active_encounter_count=sum(1 for item in encounters if item.status == "in_progress"),
            timeline_event_count=len(events),
        )
