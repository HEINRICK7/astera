"""ContextScope — clinical context hierarchy for a single request or session."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ContextScope:
    """
    The clinical context hierarchy for a single request or session.

    Hierarchy (outer → inner):
        Organization → the healthcare org (hospital, clinic)
        Workspace    → the unit or department
        Encounter    → the specific patient encounter / appointment
        Patient      → the patient identifier (de-identified where required)
        Session      → the current interaction session

    WHY this exists in Phase C (before any clinical feature):
        Every TaskOrchestrator execution receives a ContextScope.
        Every plugin receives it. Every event carries it.
        This enables multi-tenancy and LGPD compliance from Day 1.
        Adding it later would require touching every plugin interface.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str | None = None
    workspace_id: str | None = None
    encounter_id: str | None = None
    patient_id: str | None = None
    session_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def is_clinical(self) -> bool:
        """True if this scope contains any patient or encounter data."""
        return self.encounter_id is not None or self.patient_id is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id":              self.id,
            "organization_id": self.organization_id,
            "workspace_id":    self.workspace_id,
            "encounter_id":    self.encounter_id,
            "patient_id":      self.patient_id,
            "session_id":      self.session_id,
            "is_clinical":     self.is_clinical(),
        }
