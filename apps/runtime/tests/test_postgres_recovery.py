from __future__ import annotations

from types import SimpleNamespace
import unittest

from apps.runtime.src.adapters.persistence.recovery import PostgresLogicalBackup
from packages.backup_sdk import InMemoryBackupStore


class PostgresRecoveryOperatorTests(unittest.TestCase):
    def test_dump_restore_and_validation_are_traceable(self) -> None:
        calls: list[list[str]] = []

        def runner(command, **kwargs):
            calls.append(command)
            if command[0] == "pg_dump":
                return SimpleNamespace(returncode=0, stdout=b"custom-format-dump", stderr=b"")
            return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

        operator = PostgresLogicalBackup(
            backups=InMemoryBackupStore(),
            source_url="postgresql://source/astera",
            command_runner=runner,
        )
        result = operator.drill(
            target_url="postgresql://target/astera_recovery",
            validate=lambda: True,
        )

        self.assertTrue(result.validated)
        self.assertEqual(result.backup.source, "postgresql.logical")
        self.assertEqual(result.backup.size_bytes, len(b"custom-format-dump"))
        self.assertEqual(calls[0][0], "pg_dump")
        self.assertIn("--format=custom", calls[0])
        self.assertEqual(calls[1][0], "pg_restore")
        self.assertIn("--exit-on-error", calls[1])
        self.assertIn("postgresql://target/astera_recovery", calls[1])

    def test_dump_failure_is_explicit(self) -> None:
        def runner(command, **kwargs):
            return SimpleNamespace(returncode=1, stdout=b"", stderr=b"permission denied")

        operator = PostgresLogicalBackup(
            backups=InMemoryBackupStore(),
            source_url="postgresql://source/astera",
            command_runner=runner,
        )
        with self.assertRaisesRegex(RuntimeError, "pg_dump failed"):
            operator.dump()


if __name__ == "__main__":
    unittest.main()
