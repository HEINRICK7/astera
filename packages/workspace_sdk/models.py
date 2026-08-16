"""Immutable workspace contracts."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Workspace:
    workspace_id: str
    organization_id: str
    name: str
    slug: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.workspace_id, self.organization_id, self.name, self.slug)):
            raise ValueError("workspace identity fields must not be empty")

    def to_dict(self) -> dict[str, str]:
        return {
            "workspace_id": self.workspace_id,
            "organization_id": self.organization_id,
            "name": self.name,
            "slug": self.slug,
        }
