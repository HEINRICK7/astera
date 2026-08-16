"""Immutable timeline event contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    event_id: str
    organization_id: str
    patient_id: str
    event_type: str
    occurred_at: datetime
    encounter_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.event_id, self.organization_id, self.patient_id, self.event_type)):
            raise ValueError("timeline identity fields must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "organization_id": self.organization_id,
            "patient_id": self.patient_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "encounter_id": self.encounter_id,
            "payload": dict(self.payload),
        }
