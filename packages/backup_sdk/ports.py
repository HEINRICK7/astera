"""Backup persistence and verification port."""
from __future__ import annotations

from typing import Protocol

from .models import BackupArtifact


class BackupPort(Protocol):
    def create_backup(self, source: str, content: bytes) -> BackupArtifact:
        ...

    def list_backups(self) -> tuple[BackupArtifact, ...]:
        ...

    def restore(self, backup_id: str) -> bytes:
        ...
