"""Immutable encounter contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Encounter:
    encounter_id: str
    organization_id: str
    workspace_id: str
    patient_id: str
    professional_id: str
    status: str = "planned"
    started_at: datetime | None = None
    ended_at: datetime | None = None
    patient_joined_at: datetime | None = None
    consent_status: str = "pending"
    camera_ready: bool = False
    microphone_ready: bool = False

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (
            self.encounter_id,
            self.organization_id,
            self.workspace_id,
            self.patient_id,
            self.professional_id,
        )):
            raise ValueError("encounter identity fields must not be empty")
        if self.status not in {"planned", "in_progress", "completed"}:
            raise ValueError("invalid encounter status")

    def to_dict(self) -> dict[str, str | None]:
        return {
            "encounter_id": self.encounter_id,
            "organization_id": self.organization_id,
            "workspace_id": self.workspace_id,
            "patient_id": self.patient_id,
            "professional_id": self.professional_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "patient_joined_at": self.patient_joined_at.isoformat() if self.patient_joined_at else None,
            "consent_status": self.consent_status,
            "camera_ready": self.camera_ready,
            "microphone_ready": self.microphone_ready,
        }
