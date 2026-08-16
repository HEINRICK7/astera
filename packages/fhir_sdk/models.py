"""Immutable FHIR resource and bundle contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class FhirResource:
    resource_type: str
    data: Mapping[str, Any]
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not self.resource_type.strip():
            raise ValueError("resource_type must not be empty")
        if not self.data:
            raise ValueError("data must not be empty")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FhirResource":
        resource_type = data.get("resourceType")
        if not isinstance(resource_type, str):
            raise ValueError("FHIR resourceType is required")
        resource_id = data.get("id")
        if resource_id is not None and not isinstance(resource_id, str):
            raise ValueError("FHIR id must be a string")
        return cls(resource_type=resource_type, resource_id=resource_id, data=dict(data))

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.data)
        payload["resourceType"] = self.resource_type
        if self.resource_id is not None:
            payload["id"] = self.resource_id
        return payload


@dataclass(frozen=True, slots=True)
class FhirBundle:
    bundle_type: str
    entries: tuple[FhirResource, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.bundle_type.strip():
            raise ValueError("bundle_type must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "resourceType": "Bundle",
            "type": self.bundle_type,
            "total": len(self.entries),
            "entry": [{"resource": entry.to_dict()} for entry in self.entries],
            **dict(self.metadata),
        }
