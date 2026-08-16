from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from apps.runtime.src.adapters.persistence.redis import RedisRefreshSessionStore, RedisSessionStateAdapter
from apps.runtime.src.adapters.persistence.sqlalchemy import (
    PostgresAuditLog,
    PostgresEncounterRepository,
    PostgresPatientRepository,
    PostgresTimelineRepository,
    SqlDatabase,
)
from packages.auth_sdk import Principal
from packages.audit_sdk import AuditEntry


class _FakePipeline:
    def __init__(self, client: "_FakeRedis") -> None:
        self._client = client
        self._commands: list[tuple[str, str]] = []

    def get(self, key: str) -> "_FakePipeline":
        self._commands.append(("get", key))
        return self

    def delete(self, key: str) -> "_FakePipeline":
        self._commands.append(("delete", key))
        return self

    def execute(self) -> list[object]:
        result: list[object] = []
        for command, key in self._commands:
            if command == "get":
                result.append(self._client.values.get(key))
            else:
                self._client.values.pop(key, None)
                result.append(1)
        return result


class _FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    def set(self, key: str, value: str, *, ex: int) -> None:
        self.values[key] = value
        self.ttls[key] = ex

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def delete(self, key: str) -> None:
        self.values.pop(key, None)
        self.ttls.pop(key, None)

    def pipeline(self) -> _FakePipeline:
        return _FakePipeline(self)


class ProductionPersistenceAdapterTests(unittest.TestCase):
    def test_sql_state_survives_adapter_restart(self) -> None:
        with TemporaryDirectory() as directory:
            url = f"sqlite:///{Path(directory) / 'astera.db'}"
            principal = Principal(
                "doctor-1", "doctor@example.com", "org-1", ("workspace-1",)
            )
            database = SqlDatabase(url)
            patients = PostgresPatientRepository(database)
            encounters = PostgresEncounterRepository(database)
            timeline = PostgresTimelineRepository(database)
            audit = PostgresAuditLog(database)
            patient = patients.create(principal, full_name="Maria Silva")
            encounter = encounters.create(
                principal,
                workspace_id="workspace-1",
                patient_id=patient.patient_id,
            )
            timeline.append(
                principal,
                patient_id=patient.patient_id,
                encounter_id=encounter.encounter_id,
                event_type="encounter.created",
            )
            audit.append(AuditEntry.create(
                organization_id="org-1",
                actor_id="doctor-1",
                action="test",
                resource_type="patient",
            ))
            database.close()

            restarted = SqlDatabase(url)
            self.assertEqual(
                PostgresPatientRepository(restarted).get(principal, patient.patient_id).full_name,
                "Maria Silva",
            )
            self.assertEqual(
                PostgresEncounterRepository(restarted).get(principal, encounter.encounter_id).patient_id,
                patient.patient_id,
            )
            self.assertEqual(len(PostgresTimelineRepository(restarted).list_for(principal, patient.patient_id)), 1)
            self.assertEqual(len(PostgresAuditLog(restarted).list_for_organization("org-1")), 1)
            restarted.close()

    def test_redis_session_state_is_shared_and_has_ttl(self) -> None:
        client = _FakeRedis()
        first = RedisSessionStateAdapter(client, ttl_seconds=120)
        second = RedisSessionStateAdapter(client, ttl_seconds=120)
        first.save("session-1", {"status": "active"})
        self.assertEqual(second.get("session-1"), {"status": "active"})
        self.assertEqual(client.ttls["astera:session:session-1"], 120)
        second.delete("session-1")
        self.assertIsNone(first.get("session-1"))

    def test_refresh_session_is_consume_once(self) -> None:
        client = _FakeRedis()
        store = RedisRefreshSessionStore(client, ttl_seconds=60)
        principal = Principal("doctor-1", "doctor@example.com", "org-1")
        store.save("refresh-1", principal)
        self.assertEqual(store.consume("refresh-1"), principal)
        self.assertIsNone(store.consume("refresh-1"))
        self.assertNotIn("astera:refresh:refresh-1", client.values)
