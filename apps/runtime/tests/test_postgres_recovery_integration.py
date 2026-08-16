"""Opt-in Docker-backed PostgreSQL recovery drill.

Run explicitly with ``ASTERA_RUN_REAL_RECOVERY_DRILL=1`` when the local
PostgreSQL, Redis, MinIO and NATS services are available.  The test creates
and removes a uniquely named empty database; it never drops the source DB.
"""
from __future__ import annotations

import os
import subprocess
import unittest
from unittest import mock
from uuid import uuid4

from packages.auth_sdk import Principal
from packages.audit_sdk import AuditEntry


@unittest.skipUnless(
    os.getenv("ASTERA_RUN_REAL_RECOVERY_DRILL") == "1",
    "set ASTERA_RUN_REAL_RECOVERY_DRILL=1 to run the Docker-backed drill",
)
class PostgresRecoveryIntegrationTests(unittest.TestCase):
    def test_dump_restore_and_runtime_startup_against_restored_database(self) -> None:
        from apps.runtime.src.adapters.persistence.production import build_production_persistence
        from apps.runtime.src.adapters.persistence.recovery import PostgresLogicalBackup
        from apps.runtime.src.adapters.persistence.sqlalchemy import (
            PostgresAuditLog,
            PostgresEncounterRepository,
            PostgresPatientRepository,
            PostgresReviewRepository,
            SqlDatabase,
        )
        from apps.runtime.src.bootstrap.main import create_app
        from apps.runtime.src.infrastructure.settings import get_settings

        source_url = os.environ.get(
            "ASTERA_RECOVERY_SOURCE_URL",
            "postgresql+asyncpg://astera_user:astera_password@localhost:5433/astera",
        )
        source_container_url = os.environ.get(
            "ASTERA_RECOVERY_SOURCE_CONTAINER_URL",
            "postgresql://astera_user:astera_password@localhost:5432/astera",
        )
        target_database = f"astera_recovery_drill_{uuid4().hex[:12]}"
        target_host_url = source_url.rsplit("/", 1)[0] + f"/{target_database}"
        target_container_url = (
            "postgresql://astera_user:astera_password@localhost:5432/"
            f"{target_database}"
        )
        settings_env = {
            "ASTERA_ENVIRONMENT": "production",
            "ASTERA_POSTGRES_URL": target_host_url,
            "ASTERA_REDIS_URL": os.environ.get(
                "ASTERA_REDIS_URL", "redis://localhost:6380/0"
            ),
            "ASTERA_MINIO_ENDPOINT": os.environ.get(
                "ASTERA_MINIO_ENDPOINT", "http://localhost:9002"
            ),
            "ASTERA_MINIO_ACCESS_KEY": os.environ.get(
                "ASTERA_MINIO_ACCESS_KEY", "astera_admin"
            ),
            "ASTERA_MINIO_SECRET_KEY": os.environ.get(
                "ASTERA_MINIO_SECRET_KEY", "astera_minio_password"
            ),
            "ASTERA_NATS_URL": os.environ.get(
                "ASTERA_NATS_URL", "nats://localhost:4222"
            ),
            "ASTERA_AUTH_SECRET": os.environ.get(
                "ASTERA_AUTH_SECRET", "r" * 48
            ),
        }
        production = None
        target_db = None
        try:
            self._docker_database("createdb", target_database)
            get_settings.cache_clear()
            production = build_production_persistence(self._settings_for_source(source_url))
            principal = Principal(
                "recovery-drill-doctor",
                "recovery-drill@example.com",
                "recovery-org",
                ("recovery-workspace",),
            )
            patient = production.patients.create(
                principal, full_name="Recovery Drill Patient"
            )
            encounter = production.encounters.create(
                principal,
                workspace_id="recovery-workspace",
                patient_id=patient.patient_id,
            )
            production.audit.append(
                AuditEntry.create(
                    organization_id=principal.organization_id,
                    actor_id=principal.user_id,
                    action="recovery.drill.seed",
                    resource_type="encounter",
                    resource_id=encounter.encounter_id,
                    metadata={"drill": True},
                )
            )
            production.review.save_result(
                encounter.encounter_id,
                patient.patient_id,
                {"status": "pending_clinician_review", "drill": True},
            )

            operator = PostgresLogicalBackup(
                backups=production.backups,
                source_url=source_container_url,
                dump_binary=("docker", "exec", "astera_postgres", "pg_dump"),
                restore_binary=("docker", "exec", "-i", "astera_postgres", "pg_restore"),
                timeout_seconds=300,
            )
            artifact = operator.dump()
            restore_seconds = operator.restore(
                artifact.backup_id,
                target_url=target_container_url,
            )

            target_db = SqlDatabase(target_host_url)
            restored_patient = PostgresPatientRepository(target_db).get(
                principal, patient.patient_id
            )
            restored_encounter = PostgresEncounterRepository(target_db).get(
                principal, encounter.encounter_id
            )
            restored_audit = PostgresAuditLog(target_db).list_for_organization(
                principal.organization_id, action="recovery.drill.seed"
            )
            restored_review = PostgresReviewRepository(target_db).get(
                encounter.encounter_id
            )
            self.assertIsNotNone(restored_patient)
            self.assertEqual(restored_encounter.patient_id, patient.patient_id)
            self.assertEqual(
                sum(entry.resource_id == encounter.encounter_id for entry in restored_audit),
                1,
            )
            self.assertEqual(restored_review["status"], "processed")
            self.assertEqual(target_db.migration_versions(), ("001",))
            target_db.health_check()

            with mock.patch.dict(os.environ, settings_env, clear=False):
                get_settings.cache_clear()
                app = create_app()
                import asyncio

                async def start_runtime() -> None:
                    async with app.router.lifespan_context(app):
                        status = await app.state.dependencies.health()
                        self.assertTrue(all(item["ready"] for item in status.values()))

                asyncio.run(start_runtime())
            print(
                "PostgreSQL recovery drill: "
                f"backup={artifact.backup_id} checksum={artifact.checksum_sha256} "
                f"dump_seconds={operator.last_dump_seconds:.3f} "
                f"restore_seconds={restore_seconds:.3f}"
            )
        finally:
            get_settings.cache_clear()
            if target_db is not None:
                target_db.close()
            if production is not None:
                production.close()
            self._docker_database("dropdb", target_database, optional=True)

    @staticmethod
    def _docker_database(command: str, database: str, *, optional: bool = False) -> None:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "astera_postgres",
                command,
                "-U",
                "astera_user",
                database,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode and not optional:
            raise RuntimeError(result.stderr.strip() or f"docker {command} failed")

    @staticmethod
    def _settings_for_source(source_url: str):
        from apps.runtime.src.infrastructure.settings import AsteraSettings

        return AsteraSettings(
            environment="production",
            postgres_url=source_url,
            redis_url=os.environ.get("ASTERA_REDIS_URL", "redis://localhost:6380/0"),
            minio_endpoint=os.environ.get("ASTERA_MINIO_ENDPOINT", "http://localhost:9002"),
            minio_access_key=os.environ.get("ASTERA_MINIO_ACCESS_KEY", "astera_admin"),
            minio_secret_key=os.environ.get("ASTERA_MINIO_SECRET_KEY", "astera_minio_password"),
            nats_url=os.environ.get("ASTERA_NATS_URL", "nats://localhost:4222"),
            auth_secret=os.environ.get("ASTERA_AUTH_SECRET", "r" * 48),
        )
