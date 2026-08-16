"""Provider-neutral execution and certification contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProviderLifecycleStatus(str, Enum):
    DRAFT = "draft"
    IMPLEMENTED = "implemented"
    ENGINEERING_APPROVED = "engineering_approved"
    BENCHMARKED = "benchmarked"
    MEDICAL_VALIDATED = "medical_validated"
    CQA_APPROVED = "cqa_approved"
    CERTIFIED = "certified"
    PRODUCTION_READY = "production_ready"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


REQUIRED_PROVIDER_GATES: tuple[str, ...] = (
    "engineering",
    "benchmark",
    "stress_test",
    "medical_validation",
    "cqa",
    "observability",
    "documentation",
)


@dataclass(frozen=True, slots=True)
class ProviderTrace:
    """Auditable metadata for one provider execution."""

    request_id: str
    provider: str
    provider_version: str
    capability: str
    plugin: str
    kernel_version: str
    started_at: datetime
    finished_at: datetime
    latency_ms: float
    retries: int = 0
    status: str = "success"
    error: str | None = None
    confidence: float | None = None
    streaming: bool = False

    def __post_init__(self) -> None:
        for value, name in (
            (self.request_id, "request_id"),
            (self.provider, "provider"),
            (self.provider_version, "provider_version"),
            (self.capability, "capability"),
            (self.plugin, "plugin"),
            (self.kernel_version, "kernel_version"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.finished_at < self.started_at:
            raise ValueError("finished_at must not precede started_at")
        if self.latency_ms < 0 or self.retries < 0:
            raise ValueError("latency and retries must not be negative")
        if self.status not in {"success", "partial", "error"}:
            raise ValueError("unsupported provider trace status")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider": self.provider,
            "provider_version": self.provider_version,
            "capability": self.capability,
            "plugin": self.plugin,
            "kernel_version": self.kernel_version,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "latency_ms": self.latency_ms,
            "retries": self.retries,
            "status": self.status,
            "error": self.error,
            "confidence": self.confidence,
            "streaming": self.streaming,
        }


@dataclass(frozen=True, slots=True)
class ProviderExecutionResult:
    """Provider output plus the evidence needed by benchmarks and operators."""

    output: Any
    trace: ProviderTrace
    metrics: Mapping[str, Any] = field(default_factory=dict)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output = self.output.to_dict() if hasattr(self.output, "to_dict") else self.output
        return {
            "output": output,
            "trace": self.trace.to_dict(),
            "metrics": dict(self.metrics),
            "diagnostics": dict(self.diagnostics),
        }


@dataclass(frozen=True, slots=True)
class ProviderCertificationGate:
    """One evidence gate in a provider certification session."""

    name: str
    passed: bool
    evidence_refs: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("gate name must not be empty")
        if self.passed and not self.evidence_refs:
            raise ValueError("a passing provider gate requires evidence_refs")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "evidence_refs": list(self.evidence_refs),
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class ProviderCertification:
    """Lifecycle record for a provider serving one capability."""

    provider: str
    capability: str
    version: str
    gates: tuple[ProviderCertificationGate, ...] = ()
    status: ProviderLifecycleStatus = ProviderLifecycleStatus.DRAFT
    reviewer: str | None = None
    issued_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.capability.strip() or not self.version.strip():
            raise ValueError("provider, capability and version must not be empty")
        names = [gate.name for gate in self.gates]
        if len(names) != len(set(names)):
            raise ValueError("provider gate names must be unique")
        if self.status in {
            ProviderLifecycleStatus.CERTIFIED,
            ProviderLifecycleStatus.PRODUCTION_READY,
        } and (not self.reviewer or self.issued_at is None or not self.all_gates_pass()):
            raise ValueError("issued provider certifications require reviewer, timestamp and passing gates")

    def all_gates_pass(self) -> bool:
        by_name = {gate.name: gate.passed for gate in self.gates}
        return all(by_name.get(name) is True for name in REQUIRED_PROVIDER_GATES)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "capability": self.capability,
            "version": self.version,
            "status": self.status.value,
            "gates": [gate.to_dict() for gate in self.gates],
            "reviewer": self.reviewer,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "all_gates_pass": self.all_gates_pass(),
        }
