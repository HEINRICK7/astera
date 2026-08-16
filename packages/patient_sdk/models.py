"""Immutable patient contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Patient:
    patient_id: str
    organization_id: str
    full_name: str
    birth_date: date | None = None
    active: bool = True

    def __post_init__(self) -> None:
        if not self.patient_id.strip() or not self.organization_id.strip() or not self.full_name.strip():
            raise ValueError("patient identity fields must not be empty")

    def to_dict(self) -> dict[str, str | bool | None]:
        return {
            "patient_id": self.patient_id,
            "organization_id": self.organization_id,
            "full_name": self.full_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "active": self.active,
        }
