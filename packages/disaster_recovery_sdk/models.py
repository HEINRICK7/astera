"""Immutable recovery objectives and status models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class RecoveryPlan:
    service: str
    rto_minutes: int
    rpo_minutes: int
    dependencies: tuple[str, ...] = ()
    last_drill_at: datetime | None = None
    last_drill_passed: bool | None = None

    def __post_init__(self) -> None:
        if not self.service.strip() or self.rto_minutes < 0 or self.rpo_minutes < 0:
            raise ValueError("recovery plan fields are invalid")

    @property
    def status(self) -> str:
        if self.last_drill_passed is False:
            return "attention_required"
        if self.last_drill_passed is True:
            return "verified"
        return "planned"

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "rto_minutes": self.rto_minutes,
            "rpo_minutes": self.rpo_minutes,
            "dependencies": list(self.dependencies),
            "last_drill_at": self.last_drill_at.isoformat() if self.last_drill_at else None,
            "last_drill_passed": self.last_drill_passed,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class RecoveryStatus:
    plans: tuple[RecoveryPlan, ...]
    generated_at: datetime = field(default_factory=_utc_now)

    @property
    def ready(self) -> bool:
        return bool(self.plans) and all(plan.status != "attention_required" for plan in self.plans)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "plans": [plan.to_dict() for plan in self.plans],
            "generated_at": self.generated_at.isoformat(),
        }
