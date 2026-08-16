"""Immutable release record."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class ReleaseRecord:
    release_id: str
    image_tag: str
    status: str = "active"
    previous_image_tag: str | None = None
    created_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if not self.release_id.strip() or not self.image_tag.strip():
            raise ValueError("release identity fields must not be empty")
        if self.status not in {"active", "rolled_back"}:
            raise ValueError("unsupported release status")

    def to_dict(self) -> dict[str, Any]:
        return {
            "release_id": self.release_id,
            "image_tag": self.image_tag,
            "status": self.status,
            "previous_image_tag": self.previous_image_tag,
            "created_at": self.created_at.isoformat(),
        }
