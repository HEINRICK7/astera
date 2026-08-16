"""Immutable privacy and data-subject request models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class ConsentRecord:
    consent_id: str
    organization_id: str
    subject_id: str
    purpose: str
    policy_version: str
    granted: bool
    recorded_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        *,
        organization_id: str,
        subject_id: str,
        purpose: str,
        policy_version: str,
        granted: bool,
    ) -> "ConsentRecord":
        return cls(
            consent_id=uuid4().hex,
            organization_id=organization_id,
            subject_id=subject_id,
            purpose=purpose,
            policy_version=policy_version,
            granted=granted,
        )

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.consent_id, self.organization_id, self.subject_id, self.purpose, self.policy_version)):
            raise ValueError("consent identity fields must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "consent_id": self.consent_id,
            "organization_id": self.organization_id,
            "subject_id": self.subject_id,
            "purpose": self.purpose,
            "policy_version": self.policy_version,
            "granted": self.granted,
            "recorded_at": self.recorded_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class DataSubjectRequest:
    request_id: str
    organization_id: str
    subject_id: str
    request_type: str
    status: str = "received"
    requested_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        *,
        organization_id: str,
        subject_id: str,
        request_type: str,
    ) -> "DataSubjectRequest":
        return cls(
            request_id=uuid4().hex,
            organization_id=organization_id,
            subject_id=subject_id,
            request_type=request_type,
        )

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.request_id, self.organization_id, self.subject_id)):
            raise ValueError("privacy request identity fields must not be empty")
        if self.request_type not in {"access", "rectification", "erasure", "portability"}:
            raise ValueError("unsupported data subject request type")
        if self.status not in {"received", "in_progress", "completed", "rejected"}:
            raise ValueError("unsupported data subject request status")

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "organization_id": self.organization_id,
            "subject_id": self.subject_id,
            "request_type": self.request_type,
            "status": self.status,
            "requested_at": self.requested_at.isoformat(),
        }
