"""In-memory backup store used by the foundation and tests."""
from __future__ import annotations

import hashlib
from threading import RLock

from .models import BackupArtifact


class BackupIntegrityError(Exception):
    """The stored payload no longer matches its manifest checksum."""


class InMemoryBackupStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self._payloads: dict[str, bytes] = {}
        self._artifacts: dict[str, BackupArtifact] = {}

    def create_backup(self, source: str, content: bytes) -> BackupArtifact:
        payload = bytes(content)
        artifact = BackupArtifact.create(
            source=source,
            size_bytes=len(payload),
            checksum_sha256=hashlib.sha256(payload).hexdigest(),
        )
        with self._lock:
            self._payloads[artifact.backup_id] = payload
            self._artifacts[artifact.backup_id] = artifact
        return artifact

    def list_backups(self) -> tuple[BackupArtifact, ...]:
        with self._lock:
            return tuple(reversed(tuple(self._artifacts.values())))

    def restore(self, backup_id: str) -> bytes:
        with self._lock:
            artifact = self._artifacts[backup_id]
            payload = self._payloads[backup_id]
        checksum = hashlib.sha256(payload).hexdigest()
        if checksum != artifact.checksum_sha256:
            raise BackupIntegrityError(f"backup integrity check failed: {backup_id}")
        return payload
