from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from apps.runtime.src.adapters.persistence.sqlalchemy import SqlDatabase
from apps.runtime.src.infrastructure.runtime_dependencies import RuntimeDependencySupervisor


class BootstrapRecoveryHardeningTests(unittest.IsolatedAsyncioTestCase):
    async def test_startup_retries_transient_dependency_and_reports_readiness(self) -> None:
        attempts = 0

        def flaky_check() -> None:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ConnectionError("dependency warming up")

        supervisor = RuntimeDependencySupervisor(
            startup_checks={"postgres": flaky_check},
            health_checks={"postgres": flaky_check},
            retries=3,
            backoff_seconds=0,
        )

        await supervisor.start()

        self.assertEqual(attempts, 3)
        self.assertTrue(await supervisor.is_ready())
        self.assertEqual((await supervisor.health())["postgres"]["ready"], True)
        await supervisor.close()

    async def test_failed_critical_dependency_blocks_startup(self) -> None:
        supervisor = RuntimeDependencySupervisor(
            startup_checks={"redis": lambda: (_ for _ in ()).throw(ConnectionError("offline"))},
            retries=2,
            backoff_seconds=0,
        )

        with self.assertRaisesRegex(RuntimeError, "redis"):
            await supervisor.start()
        self.assertFalse(await supervisor.is_ready())

    async def test_close_runs_callbacks_in_reverse_order(self) -> None:
        calls: list[str] = []

        supervisor = RuntimeDependencySupervisor(
            close_callbacks=(lambda: calls.append("postgres"), lambda: calls.append("redis")),
        )
        await supervisor.close()

        self.assertEqual(calls, ["redis", "postgres"])


class VersionedMigrationTests(unittest.TestCase):
    def test_schema_is_versioned_and_upgrade_is_idempotent(self) -> None:
        with TemporaryDirectory() as directory:
            url = f"sqlite:///{Path(directory) / 'astera.db'}"
            first = SqlDatabase(url)
            self.assertEqual(first.migration_versions(), ("001",))
            first.close()

            second = SqlDatabase(url)
            self.assertEqual(second.migration_versions(), ("001",))
            second.close()


if __name__ == "__main__":
    unittest.main()
