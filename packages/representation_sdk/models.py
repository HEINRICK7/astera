"""Immutable representation contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class RepresentationRequest:
    record_id: str
    encounter_id: str
    version: str
    statements: tuple[str, ...]
    formats: tuple[str, ...]
    context_id: str | None = None
    context_version: int | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    patient_id: str | None = None
    facts: tuple[Mapping[str, Any], ...] = ()
    transcript: Mapping[str, Any] | None = None
    reasoning: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.record_id.strip() or not self.encounter_id.strip() or not self.version.strip():
            raise ValueError("record identity and version must not be empty")
        if not self.statements:
            raise ValueError("statements must not be empty")
        if not self.formats:
            raise ValueError("formats must not be empty")
        if any(format_name not in {"soap", "fhir", "summary"} for format_name in self.formats):
            raise ValueError("unsupported representation format")
        if self.context_version is not None and self.context_version < 1:
            raise ValueError("context_version must be at least 1")


@dataclass(frozen=True, slots=True)
class Representation:
    format: str
    content: Any
    source_record_id: str
    version: str
    context_id: str | None = None
    context_version: int | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": self.format,
            "content": self.content,
            "source_record_id": self.source_record_id,
            "version": self.version,
            "context_id": self.context_id,
            "context_version": self.context_version,
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True, slots=True)
class RepresentationResult:
    record_id: str
    representations: tuple[Representation, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "representations": [item.to_dict() for item in self.representations],
        }
