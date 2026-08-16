"""Development encounter directory behind the future persistent adapter."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from packages.auth_sdk import AuthorizationError, Principal

from .models import Encounter


class InMemoryEncounterRepository:
    """Development adapter for encounter lifecycle and tenant checks."""

    def __init__(self) -> None:
        self._encounters: dict[str, Encounter] = {}

    def create(self, principal: Principal, *, workspace_id: str, patient_id: str) -> Encounter:
        self._require_workspace(principal, workspace_id)
        encounter = Encounter(
            encounter_id=f"encounter-{uuid4().hex[:12]}",
            organization_id=principal.organization_id,
            workspace_id=workspace_id,
            patient_id=patient_id,
            professional_id=principal.user_id,
        )
        self._encounters[encounter.encounter_id] = encounter
        return encounter

    def start(self, principal: Principal, encounter_id: str) -> Encounter:
        encounter = self._get_for(principal, encounter_id)
        if encounter.status != "planned":
            raise ValueError("only planned encounters can start")
        updated = replace(encounter, status="in_progress", started_at=datetime.now(timezone.utc))
        self._encounters[encounter_id] = updated
        return updated

    def complete(self, principal: Principal, encounter_id: str) -> Encounter:
        encounter = self._get_for(principal, encounter_id)
        if encounter.status != "in_progress":
            raise ValueError("only in-progress encounters can complete")
        updated = replace(encounter, status="completed", ended_at=datetime.now(timezone.utc))
        self._encounters[encounter_id] = updated
        return updated

    def get(self, principal: Principal, encounter_id: str) -> Encounter:
        return self._get_for(principal, encounter_id)

    def get_public(self, encounter_id: str) -> Encounter:
        """Resolve a development invite link without professional auth."""
        encounter = self._encounters.get(encounter_id)
        if encounter is None:
            raise KeyError("encounter not found")
        return encounter

    def patient_join(self, encounter_id: str) -> Encounter:
        encounter = self.get_public(encounter_id)
        updated = replace(encounter, patient_joined_at=datetime.now(timezone.utc))
        self._encounters[encounter_id] = updated
        return updated

    def patient_consent(self, encounter_id: str, *, accepted: bool) -> Encounter:
        encounter = self.get_public(encounter_id)
        updated = replace(encounter, consent_status="accepted" if accepted else "denied")
        self._encounters[encounter_id] = updated
        return updated

    def patient_equipment(self, encounter_id: str, *, camera_ready: bool, microphone_ready: bool) -> Encounter:
        encounter = self.get_public(encounter_id)
        updated = replace(encounter, camera_ready=camera_ready, microphone_ready=microphone_ready)
        self._encounters[encounter_id] = updated
        return updated

    def list_for(self, principal: Principal) -> tuple[Encounter, ...]:
        return tuple(
            encounter
            for encounter in self._encounters.values()
            if encounter.organization_id == principal.organization_id
            and encounter.professional_id == principal.user_id
            and encounter.workspace_id in principal.workspace_ids
        )

    def _get_for(self, principal: Principal, encounter_id: str) -> Encounter:
        encounter = self._encounters.get(encounter_id)
        if encounter is None or encounter.organization_id != principal.organization_id:
            raise KeyError("encounter not found")
        self._require_workspace(principal, encounter.workspace_id)
        if encounter.professional_id != principal.user_id:
            raise AuthorizationError("professional is not assigned to encounter")
        return encounter

    @staticmethod
    def _require_workspace(principal: Principal, workspace_id: str) -> None:
        if workspace_id not in principal.workspace_ids:
            raise AuthorizationError("professional is not a workspace member")


# Compatibility name for callers migrating from the original directory API.
EncounterDirectory = InMemoryEncounterRepository
