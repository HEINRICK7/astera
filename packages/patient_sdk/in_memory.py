"""Development patient directory behind the future persistent adapter."""
from __future__ import annotations

from uuid import uuid4

from packages.auth_sdk import Principal

from .models import Patient


class InMemoryPatientRepository:
    """Development adapter for patient records with tenant isolation."""

    def __init__(self) -> None:
        self._patients: dict[str, Patient] = {}

    def register(self, patient: Patient) -> None:
        """Register a deterministic development fixture without generating an ID."""
        self._patients[patient.patient_id] = patient

    def create(self, principal: Principal, *, full_name: str) -> Patient:
        patient = Patient(
            patient_id=f"patient-{uuid4().hex[:12]}",
            organization_id=principal.organization_id,
            full_name=full_name,
        )
        self._patients[patient.patient_id] = patient
        return patient

    def get(self, principal: Principal, patient_id: str) -> Patient | None:
        patient = self._patients.get(patient_id)
        if patient is None or patient.organization_id != principal.organization_id:
            return None
        return patient

    def list_for(self, principal: Principal) -> tuple[Patient, ...]:
        return tuple(
            patient
            for patient in self._patients.values()
            if patient.organization_id == principal.organization_id
        )


# Compatibility name for callers migrating from the original directory API.
PatientDirectory = InMemoryPatientRepository
