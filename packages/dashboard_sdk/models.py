"""Immutable dashboard snapshot contract."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    organization_id: str
    workspace_ids: tuple[str, ...]
    patient_count: int
    encounter_count: int
    active_encounter_count: int
    timeline_event_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "organization_id": self.organization_id,
            "workspace_ids": list(self.workspace_ids),
            "patient_count": self.patient_count,
            "encounter_count": self.encounter_count,
            "active_encounter_count": self.active_encounter_count,
            "timeline_event_count": self.timeline_event_count,
        }
