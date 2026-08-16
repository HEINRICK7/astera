"""Operational PostgreSQL logical backup and restore adapter."""
from __future__ import annotations

from dataclasses import dataclass
import subprocess
from time import monotonic
from typing import Any, Callable, Sequence

from packages.backup_sdk import BackupArtifact

CommandRunner = Callable[..., Any]


@dataclass(frozen=True, slots=True)
class RecoveryDrillResult:
    backup: BackupArtifact
    dump_seconds: float
    restore_seconds: float
    validated: bool


class PostgresLogicalBackup:
    """Run pg_dump/pg_restore while keeping artifacts in the backup boundary."""

    def __init__(
        self,
        *,
        backups: Any,
        source_url: str,
        dump_binary: str | Sequence[str] = "pg_dump",
        restore_binary: str | Sequence[str] = "pg_restore",
        timeout_seconds: int = 300,
        command_runner: CommandRunner = subprocess.run,
    ) -> None:
        self._backups = backups
        self._source_url = source_url
        self._dump_binary = dump_binary
        self._restore_binary = restore_binary
        self._timeout_seconds = timeout_seconds
        self._run = command_runner
        self.last_dump_seconds = 0.0

    def dump(self) -> BackupArtifact:
        started = monotonic()
        result = self._run(
            [
                *self._command(self._dump_binary),
                "--format=custom",
                "--no-owner",
                "--no-privileges",
                "--dbname",
                self._cli_url(self._source_url),
            ],
            capture_output=True,
            check=False,
            timeout=self._timeout_seconds,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {self._stderr(result)}")
        payload = bytes(result.stdout or b"")
        if not payload:
            raise RuntimeError("pg_dump produced an empty artifact")
        artifact = self._backups.create_backup("postgresql.logical", payload)
        self.last_dump_seconds = monotonic() - started
        return artifact

    def restore(self, backup_id: str, *, target_url: str) -> float:
        payload = self._backups.restore(backup_id)
        started = monotonic()
        # Read the custom-format artifact from stdin. This works when the
        # restore process runs in a separate container and avoids assuming a
        # shared host/container temporary directory.
        result = self._run(
            [
                *self._command(self._restore_binary),
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                "--dbname",
                self._cli_url(target_url),
            ],
            input=payload,
            capture_output=True,
            check=False,
            timeout=self._timeout_seconds,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pg_restore failed: {self._stderr(result)}")
        return monotonic() - started

    def drill(
        self,
        *,
        target_url: str,
        validate: Callable[[], bool],
    ) -> RecoveryDrillResult:
        backup = self.dump()
        restore_seconds = self.restore(backup.backup_id, target_url=target_url)
        validated = bool(validate())
        if not validated:
            raise RuntimeError(f"recovery validation failed for {backup.backup_id}")
        return RecoveryDrillResult(
            backup=backup,
            dump_seconds=self.last_dump_seconds,
            restore_seconds=restore_seconds,
            validated=True,
        )

    @staticmethod
    def _stderr(result: Any) -> str:
        error = result.stderr or b"unknown error"
        return error.decode(errors="replace") if isinstance(error, bytes) else str(error)

    @staticmethod
    def _command(binary: str | Sequence[str]) -> list[str]:
        return [binary] if isinstance(binary, str) else list(binary)

    @staticmethod
    def _cli_url(url: str) -> str:
        """Convert SQLAlchemy driver URLs to URLs understood by libpq tools."""
        return url.replace("postgresql+asyncpg://", "postgresql://", 1).replace(
            "postgresql+psycopg://", "postgresql://", 1
        )
