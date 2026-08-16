"""Immutable backup manifest model."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class BackupArtifact:
    backup_id: str
    source: str
    size_bytes: int
    checksum_sha256: str
    status: str = "available"
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(cls, *, source: str, size_bytes: int, checksum_sha256: str) -> "BackupArtifact":
        return cls(
            backup_id=uuid4().hex,
            source=source,
            size_bytes=size_bytes,
            checksum_sha256=checksum_sha256,
        )

    def __post_init__(self) -> None:
        if not self.backup_id.strip() or not self.source.strip() or not self.checksum_sha256.strip():
            raise ValueError("backup identity fields must not be empty")
        if self.size_bytes < 0:
            raise ValueError("backup size must not be negative")
        if self.status not in {"available", "verified", "corrupt"}:
            raise ValueError("unsupported backup status")

    def to_dict(self) -> dict[str, Any]:
        return {
            "backup_id": self.backup_id,
            "source": self.source,
            "size_bytes": self.size_bytes,
            "checksum_sha256": self.checksum_sha256,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
