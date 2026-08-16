"""Persistence and state ports owned by the Astera application boundary."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping, Protocol, runtime_checkable

from packages.auth_sdk import AuthTokens, LoginCredentials, Principal
from packages.audit_sdk import AuditEntry
from packages.encounter_sdk import Encounter
from packages.patient_sdk import Patient
from packages.timeline_sdk import TimelineEvent
from packages.workspace_sdk import Workspace



@runtime_checkable
class AuthenticationPort(Protocol):
    """Authentication facade; credential/session storage stays behind it."""

    def register_user(self, credentials: LoginCredentials, principal: Principal) -> None:
        ...

    def login(self, credentials: LoginCredentials) -> AuthTokens:
        ...

    def refresh(self, refresh_token: str) -> AuthTokens:
        ...

    def authenticate(self, access_token: str) -> Principal:
        ...

    def require_permission(self, principal: Principal, permission: str) -> None:
        ...


@runtime_checkable
class CredentialStorePort(Protocol):
    """Durable credential ownership, separate from token/session concerns."""

    def register_user(self, credentials: LoginCredentials, principal: Principal) -> None:
        ...

    def authenticate_credentials(self, credentials: LoginCredentials) -> Principal:
        ...


@runtime_checkable
class SessionStorePort(Protocol):
    """Revocable refresh/session state, not a durable clinical record."""

    def save(self, session_id: str, principal: Principal) -> None:
        ...

    def consume(self, session_id: str) -> Principal | None:
        ...


@runtime_checkable
class TokenIssuerPort(Protocol):
    """Access-token issuance and verification boundary."""

    def issue(self, principal: Principal) -> AuthTokens:
        ...

    def verify(self, access_token: str) -> Principal:
        ...


@runtime_checkable
class PatientRepositoryPort(Protocol):
    def create(self, principal: Principal, *, full_name: str) -> Patient:
        ...

    def get(self, principal: Principal, patient_id: str) -> Patient | None:
        ...

    def list_for(self, principal: Principal) -> tuple[Patient, ...]:
        ...


@runtime_checkable
class EncounterRepositoryPort(Protocol):
    def create(self, principal: Principal, *, workspace_id: str, patient_id: str) -> Encounter:
        ...

    def get(self, principal: Principal, encounter_id: str) -> Encounter:
        ...

    def list_for(self, principal: Principal) -> tuple[Encounter, ...]:
        ...

    def get_public(self, encounter_id: str) -> Encounter:
        ...

    def start(self, principal: Principal, encounter_id: str) -> Encounter:
        ...

    def complete(self, principal: Principal, encounter_id: str) -> Encounter:
        ...

    def patient_join(self, encounter_id: str) -> Encounter:
        ...

    def patient_consent(self, encounter_id: str, *, accepted: bool) -> Encounter:
        ...

    def patient_equipment(self, encounter_id: str, *, camera_ready: bool, microphone_ready: bool) -> Encounter:
        ...


@runtime_checkable
class WorkspaceRepositoryPort(Protocol):
    def list_for(self, principal: Principal) -> tuple[Workspace, ...]:
        ...

    def get(self, workspace_id: str) -> Workspace | None:
        ...


@runtime_checkable
class TimelineRepositoryPort(Protocol):
    def append(
        self,
        principal: Principal,
        *,
        patient_id: str,
        event_type: str,
        encounter_id: str | None = None,
        payload: dict[str, object] | None = None,
        occurred_at: datetime | None = None,
    ) -> TimelineEvent:
        ...

    def list_for(self, principal: Principal, patient_id: str) -> tuple[TimelineEvent, ...]:
        ...


@runtime_checkable
class AuditLogPort(Protocol):
    def append(self, entry: AuditEntry) -> None:
        ...

    def list_for_organization(
        self,
        organization_id: str,
        *,
        limit: int = 100,
        action: str | None = None,
    ) -> tuple[AuditEntry, ...]:
        ...


@runtime_checkable
class ReviewRepositoryPort(Protocol):
    def get(self, encounter_id: str) -> dict[str, Any] | None:
        ...

    def list_for(self, patient_id: str | None = None) -> list[dict[str, Any]]:
        ...

    def begin(self, encounter_id: str, patient_id: str) -> None:
        ...

    def record(self, event: Any) -> None:
        ...

    def set_representation(self, encounter_id: str, format_name: str, content: Any) -> None:
        ...

    def complete(self, encounter_id: str, status: str = "completed") -> None:
        ...

    def save_result(self, encounter_id: str, patient_id: str, result: dict[str, Any]) -> None:
        ...


@runtime_checkable
class ClinicalEvidenceStorePort(Protocol):
    def apply(self, batch: Any, *, source: str) -> Any:
        ...


@runtime_checkable
class EvidenceObjectStorePort(Protocol):
    """Durable raw-evidence/object boundary, distinct from clinical projections."""

    def put(self, object_key: str, payload: bytes, *, content_type: str, metadata: Mapping[str, str]) -> None:
        ...

    def get(self, object_key: str) -> bytes | None:
        ...


@runtime_checkable
class SessionStatePort(Protocol):
    """Ephemeral/recoverable session state, not a durable clinical record."""

    def get(self, session_id: str) -> Mapping[str, Any] | None:
        ...

    def save(self, session_id: str, state: Mapping[str, Any]) -> None:
        ...

    def delete(self, session_id: str) -> None:
        ...


# Compatibility names retained while callers migrate to responsibility-based names.
AuditRepositoryPort = AuditLogPort
ClinicalReviewRepositoryPort = ReviewRepositoryPort
