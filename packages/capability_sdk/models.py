"""Immutable contracts for capability certification."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class GateStatus(str, Enum):
    NOT_RUN = "not_run"
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"


class CertificationStatus(str, Enum):
    ENGINEERING_COMPLETE = "engineering_complete"
    VALIDATION_IN_PROGRESS = "validation_in_progress"
    CERTIFIED = "certified"
    PRODUCTION_READY = "production_ready"
    NOT_ISSUED = "not_issued"


REQUIRED_GATES: tuple[str, ...] = (
    "engineering",
    "medical_validation",
    "cqa",
    "regression",
    "performance",
    "security",
    "observability",
    "documentation",
)


@dataclass(frozen=True, slots=True)
class CapabilityGate:
    gate: str
    status: GateStatus
    evidence_refs: tuple[str, ...] = ()
    reviewer: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.gate.strip():
            raise ValueError("gate must not be empty")
        if self.status == GateStatus.PASS and not self.evidence_refs:
            raise ValueError("a passing gate must have evidence_refs")

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "status": self.status.value,
            "evidence_refs": list(self.evidence_refs),
            "reviewer": self.reviewer,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class CapabilityCertification:
    capability: str
    version: str
    providers: tuple[str, ...]
    gates: tuple[CapabilityGate, ...]
    status: CertificationStatus = CertificationStatus.NOT_ISSUED
    constraints: tuple[str, ...] = ()
    reviewer: str | None = None
    issued_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.capability.strip() or not self.version.strip():
            raise ValueError("capability and version must not be empty")
        if not self.providers or any(not provider.strip() for provider in self.providers):
            raise ValueError("at least one provider is required")
        gate_names = [gate.gate for gate in self.gates]
        if len(gate_names) != len(set(gate_names)):
            raise ValueError("gate names must be unique")
        if self.status == CertificationStatus.PRODUCTION_READY and not self.is_production_ready():
            raise ValueError("Production Ready requires every mandatory gate to pass")
        if self.status in {CertificationStatus.CERTIFIED, CertificationStatus.PRODUCTION_READY}:
            if self.issued_at is None or not self.reviewer:
                raise ValueError("issued certifications require reviewer and issued_at")

    def is_production_ready(self) -> bool:
        by_name = {gate.gate: gate.status for gate in self.gates}
        return all(by_name.get(name) == GateStatus.PASS for name in REQUIRED_GATES)

    def missing_gates(self) -> tuple[str, ...]:
        by_name = {gate.gate: gate.status for gate in self.gates}
        return tuple(name for name in REQUIRED_GATES if by_name.get(name) != GateStatus.PASS)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "version": self.version,
            "providers": list(self.providers),
            "gates": [gate.to_dict() for gate in self.gates],
            "status": self.status.value,
            "constraints": list(self.constraints),
            "reviewer": self.reviewer,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "metadata": dict(self.metadata),
            "production_ready": self.is_production_ready(),
            "missing_gates": list(self.missing_gates()),
        }


def certification_timestamp() -> datetime:
    """Return an explicit UTC timestamp for a future certification record."""
    return datetime.now(timezone.utc)
