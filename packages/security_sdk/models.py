"""Immutable security posture report models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class SecurityCheck:
    name: str
    status: str
    detail: str

    def __post_init__(self) -> None:
        if self.status not in {"pass", "warn", "fail"}:
            raise ValueError("unsupported security check status")

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class SecurityReport:
    environment: str
    checks: tuple[SecurityCheck, ...]
    generated_at: datetime = field(default_factory=_utc_now)

    @property
    def passed(self) -> bool:
        return all(check.status != "fail" for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "environment": self.environment,
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.checks],
            "generated_at": self.generated_at.isoformat(),
        }
