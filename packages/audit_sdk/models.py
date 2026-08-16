"""Immutable audit record with explicit tenant and actor scope."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """A redacted record of a security or business-relevant action."""

    entry_id: str
    organization_id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str | None = None
    outcome: str = "success"
    metadata: tuple[tuple[str, str], ...] = ()
    occurred_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        required = (
            self.entry_id,
            self.organization_id,
            self.actor_id,
            self.action,
            self.resource_type,
        )
        if any(not value.strip() for value in required):
            raise ValueError("audit identity fields must not be empty")
        if self.outcome not in {"success", "failure", "denied"}:
            raise ValueError("unsupported audit outcome")

    @classmethod
    def create(
        cls,
        *,
        organization_id: str,
        actor_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        outcome: str = "success",
        metadata: Mapping[str, Any] | None = None,
    ) -> "AuditEntry":
        return cls(
            entry_id=uuid4().hex,
            organization_id=organization_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            metadata=tuple(
                sorted((str(key), _redact(str(key), str(value))) for key, value in (metadata or {}).items())
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "organization_id": self.organization_id,
            "actor_id": self.actor_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "outcome": self.outcome,
            "metadata": dict(self.metadata),
            "occurred_at": self.occurred_at.isoformat(),
        }


_SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token", "secret"}


def _redact(key: str, value: str) -> str:
    return "[REDACTED]" if key.lower() in _SENSITIVE_KEYS else value
