"""SQLAlchemy persistence adapters for durable Astera state.

The module imports SQLAlchemy lazily so development and unit-test bootstraps
can continue using in-memory adapters when production dependencies are absent.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace
from typing import Any

from packages.auth_sdk import AuthenticationError, InMemoryCredentialStore, LoginCredentials, Principal
from packages.audit_sdk import AuditEntry
from packages.backup_sdk import BackupArtifact
from packages.disaster_recovery_sdk import RecoveryPlan, RecoveryStatus
from packages.encounter_sdk import Encounter
from packages.patient_sdk import Patient
from packages.privacy_sdk import ConsentRecord, DataSubjectRequest
from packages.timeline_sdk import TimelineEvent
from packages.workspace_sdk import Workspace

from apps.runtime.src.infrastructure.migrations import MigrationRunner, initial_metadata_migration

from .clinical_review import InMemoryClinicalReviewStore


class SqlDatabase:
    """Own the SQLAlchemy engine, schema and transaction boundary."""

    def __init__(self, url: str) -> None:
        try:
            from sqlalchemy import (
                JSON,
                Boolean,
                Column,
                Date,
                DateTime,
                Integer,
                LargeBinary,
                MetaData,
                String,
                Table,
                Text,
                and_,
                create_engine,
                insert,
                select,
                update,
            )
        except ImportError as exc:  # pragma: no cover - exercised in deployment
            raise RuntimeError(
                "Production persistence requires SQLAlchemy and psycopg; install requirements.txt"
            ) from exc

        normalized_url = url
        if normalized_url.startswith("postgresql+asyncpg://"):
            normalized_url = normalized_url.replace(
                "postgresql+asyncpg://", "postgresql+psycopg://", 1
            )
        elif normalized_url.startswith("postgresql://"):
            normalized_url = normalized_url.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        self.url = normalized_url
        self.engine = create_engine(
            normalized_url,
            future=True,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
        self.sa = SimpleNamespace(
            and_=and_,
            insert=insert,
            select=select,
            update=update,
        )
        metadata = MetaData()
        self.metadata = metadata
        self.tables = {
            "patients": Table(
                "patients", metadata,
                Column("patient_id", String(128), primary_key=True),
                Column("organization_id", String(128), nullable=False, index=True),
                Column("full_name", Text, nullable=False),
                Column("birth_date", Date, nullable=True),
                Column("active", Boolean, nullable=False, default=True),
            ),
            "workspaces": Table(
                "workspaces", metadata,
                Column("workspace_id", String(128), primary_key=True),
                Column("organization_id", String(128), nullable=False, index=True),
                Column("name", Text, nullable=False),
                Column("slug", String(255), nullable=False),
            ),
            "encounters": Table(
                "encounters", metadata,
                Column("encounter_id", String(128), primary_key=True),
                Column("organization_id", String(128), nullable=False, index=True),
                Column("workspace_id", String(128), nullable=False, index=True),
                Column("patient_id", String(128), nullable=False, index=True),
                Column("professional_id", String(128), nullable=False, index=True),
                Column("status", String(32), nullable=False),
                Column("started_at", DateTime(timezone=True), nullable=True),
                Column("ended_at", DateTime(timezone=True), nullable=True),
                Column("patient_joined_at", DateTime(timezone=True), nullable=True),
                Column("consent_status", String(32), nullable=False),
                Column("camera_ready", Boolean, nullable=False),
                Column("microphone_ready", Boolean, nullable=False),
            ),
            "timeline_events": Table(
                "timeline_events", metadata,
                Column("event_id", String(128), primary_key=True),
                Column("organization_id", String(128), nullable=False, index=True),
                Column("patient_id", String(128), nullable=False, index=True),
                Column("event_type", String(255), nullable=False),
                Column("occurred_at", DateTime(timezone=True), nullable=False),
                Column("encounter_id", String(128), nullable=True, index=True),
                Column("payload", JSON, nullable=False),
            ),
            "audit_entries": Table(
                "audit_entries", metadata,
                Column("entry_id", String(128), primary_key=True),
                Column("organization_id", String(128), nullable=False, index=True),
                Column("actor_id", String(128), nullable=False),
                Column("action", String(255), nullable=False, index=True),
                Column("resource_type", String(255), nullable=False),
                Column("resource_id", String(255), nullable=True),
                Column("outcome", String(32), nullable=False),
                Column("metadata", JSON, nullable=False),
                Column("occurred_at", DateTime(timezone=True), nullable=False),
            ),
            "review_records": Table(
                "review_records", metadata,
                Column("encounter_id", String(128), primary_key=True),
                Column("patient_id", String(128), nullable=True, index=True),
                Column("status", String(32), nullable=False),
                Column("record", JSON, nullable=False),
                Column("updated_at", DateTime(timezone=True), nullable=False),
            ),
            "credentials": Table(
                "credentials", metadata,
                Column("email", String(320), primary_key=True),
                Column("password_hash", LargeBinary, nullable=False),
                Column("principal", JSON, nullable=False),
            ),
            "privacy_consents": Table(
                "privacy_consents", metadata,
                Column("consent_id", String(128), primary_key=True),
                Column("organization_id", String(128), nullable=False, index=True),
                Column("subject_id", String(128), nullable=False, index=True),
                Column("purpose", Text, nullable=False),
                Column("policy_version", String(128), nullable=False),
                Column("granted", Boolean, nullable=False),
                Column("recorded_at", DateTime(timezone=True), nullable=False),
            ),
            "privacy_requests": Table(
                "privacy_requests", metadata,
                Column("request_id", String(128), primary_key=True),
                Column("organization_id", String(128), nullable=False, index=True),
                Column("subject_id", String(128), nullable=False, index=True),
                Column("request_type", String(32), nullable=False),
                Column("status", String(32), nullable=False),
                Column("requested_at", DateTime(timezone=True), nullable=False),
            ),
            "backup_artifacts": Table(
                "backup_artifacts", metadata,
                Column("backup_id", String(128), primary_key=True),
                Column("source", Text, nullable=False),
                Column("size_bytes", Integer, nullable=False),
                Column("checksum_sha256", String(128), nullable=False),
                Column("status", String(32), nullable=False),
                Column("created_at", DateTime(timezone=True), nullable=False),
                Column("object_key", String(255), nullable=False, unique=True),
            ),
            "recovery_plans": Table(
                "recovery_plans", metadata,
                Column("service", String(255), primary_key=True),
                Column("rto_minutes", Integer, nullable=False),
                Column("rpo_minutes", Integer, nullable=False),
                Column("dependencies", JSON, nullable=False),
                Column("last_drill_at", DateTime(timezone=True), nullable=True),
                Column("last_drill_passed", Boolean, nullable=True),
            ),
        }
        self.migrations = MigrationRunner(
            self.engine,
            metadata,
            migrations=(initial_metadata_migration(metadata),),
        )
        self.migrations.upgrade()

    def close(self) -> None:
        self.engine.dispose()

    def health_check(self) -> None:
        with self.engine.connect() as connection:
            connection.execute(self.sa.select(self.tables["patients"].c.patient_id).limit(1))

    def migration_versions(self) -> tuple[str, ...]:
        return self.migrations.applied_versions()


class PostgresPatientRepository:
    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._table = database.tables["patients"]

    def create(self, principal: Principal, *, full_name: str) -> Patient:
        from uuid import uuid4

        patient = Patient(
            patient_id=f"patient-{uuid4().hex[:12]}",
            organization_id=principal.organization_id,
            full_name=full_name,
        )
        with self._db.engine.begin() as connection:
            values = patient.to_dict()
            values["birth_date"] = patient.birth_date
            connection.execute(self._table.insert().values(**values))
        return patient

    def register(self, patient: Patient) -> None:
        with self._db.engine.begin() as connection:
            values = patient.to_dict()
            values["birth_date"] = patient.birth_date
            connection.execute(self._table.insert().values(**values))

    def get(self, principal: Principal, patient_id: str) -> Patient | None:
        with self._db.engine.connect() as connection:
            row = connection.execute(
                self._db.sa.select(self._table).where(
                    self._db.sa.and_(
                        self._table.c.patient_id == patient_id,
                        self._table.c.organization_id == principal.organization_id,
                    )
                )
            ).mappings().first()
        return _patient(row) if row else None

    def list_for(self, principal: Principal) -> tuple[Patient, ...]:
        with self._db.engine.connect() as connection:
            rows = connection.execute(
                self._db.sa.select(self._table).where(
                    self._table.c.organization_id == principal.organization_id
                ).order_by(self._table.c.patient_id)
            ).mappings()
            return tuple(_patient(row) for row in rows)


class PostgresWorkspaceRepository:
    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._table = database.tables["workspaces"]

    def register(self, workspace: Workspace) -> None:
        with self._db.engine.begin() as connection:
            connection.execute(self._table.insert().values(**workspace.to_dict()))

    def list_for(self, principal: Principal) -> tuple[Workspace, ...]:
        with self._db.engine.connect() as connection:
            rows = connection.execute(
                self._db.sa.select(self._table).where(
                    self._db.sa.and_(
                        self._table.c.organization_id == principal.organization_id,
                        self._table.c.workspace_id.in_(principal.workspace_ids),
                    )
                ).order_by(self._table.c.workspace_id)
            ).mappings()
            return tuple(_workspace(row) for row in rows)

    def get(self, workspace_id: str) -> Workspace | None:
        with self._db.engine.connect() as connection:
            row = connection.execute(
                self._db.sa.select(self._table).where(self._table.c.workspace_id == workspace_id)
            ).mappings().first()
        return _workspace(row) if row else None


class PostgresEncounterRepository:
    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._table = database.tables["encounters"]

    def create(self, principal: Principal, *, workspace_id: str, patient_id: str) -> Encounter:
        from uuid import uuid4

        if workspace_id not in principal.workspace_ids:
            from packages.auth_sdk import AuthorizationError
            raise AuthorizationError("professional is not a workspace member")
        encounter = Encounter(
            encounter_id=f"encounter-{uuid4().hex[:12]}",
            organization_id=principal.organization_id,
            workspace_id=workspace_id,
            patient_id=patient_id,
            professional_id=principal.user_id,
        )
        with self._db.engine.begin() as connection:
            connection.execute(self._table.insert().values(
                encounter_id=encounter.encounter_id,
                organization_id=encounter.organization_id,
                workspace_id=encounter.workspace_id,
                patient_id=encounter.patient_id,
                professional_id=encounter.professional_id,
                **_encounter_values(encounter),
            ))
        return encounter

    def get(self, principal: Principal, encounter_id: str) -> Encounter:
        encounter = self._get_for(principal, encounter_id)
        return encounter

    def get_public(self, encounter_id: str) -> Encounter:
        with self._db.engine.connect() as connection:
            row = connection.execute(
                self._db.sa.select(self._table).where(self._table.c.encounter_id == encounter_id)
            ).mappings().first()
        if not row:
            raise KeyError("encounter not found")
        return _encounter(row)

    def list_for(self, principal: Principal) -> tuple[Encounter, ...]:
        with self._db.engine.connect() as connection:
            rows = connection.execute(
                self._db.sa.select(self._table).where(
                    self._db.sa.and_(
                        self._table.c.organization_id == principal.organization_id,
                        self._table.c.professional_id == principal.user_id,
                        self._table.c.workspace_id.in_(principal.workspace_ids),
                    )
                ).order_by(self._table.c.encounter_id)
            ).mappings()
            return tuple(_encounter(row) for row in rows)

    def start(self, principal: Principal, encounter_id: str) -> Encounter:
        encounter = self._get_for(principal, encounter_id)
        if encounter.status != "planned":
            raise ValueError("only planned encounters can start")
        return self._update(encounter_id, status="in_progress", started_at=datetime.now(timezone.utc))

    def complete(self, principal: Principal, encounter_id: str) -> Encounter:
        encounter = self._get_for(principal, encounter_id)
        if encounter.status != "in_progress":
            raise ValueError("only in-progress encounters can complete")
        return self._update(encounter_id, status="completed", ended_at=datetime.now(timezone.utc))

    def patient_join(self, encounter_id: str) -> Encounter:
        self.get_public(encounter_id)
        return self._update(encounter_id, patient_joined_at=datetime.now(timezone.utc))

    def patient_consent(self, encounter_id: str, *, accepted: bool) -> Encounter:
        self.get_public(encounter_id)
        return self._update(encounter_id, consent_status="accepted" if accepted else "denied")

    def patient_equipment(self, encounter_id: str, *, camera_ready: bool, microphone_ready: bool) -> Encounter:
        self.get_public(encounter_id)
        return self._update(encounter_id, camera_ready=camera_ready, microphone_ready=microphone_ready)

    def _get_for(self, principal: Principal, encounter_id: str) -> Encounter:
        encounter = self.get_public(encounter_id)
        from packages.auth_sdk import AuthorizationError
        if encounter.organization_id != principal.organization_id:
            raise KeyError("encounter not found")
        if encounter.workspace_id not in principal.workspace_ids:
            raise AuthorizationError("professional is not a workspace member")
        if encounter.professional_id != principal.user_id:
            raise AuthorizationError("professional is not assigned to encounter")
        return encounter

    def _update(self, encounter_id: str, **values: Any) -> Encounter:
        with self._db.engine.begin() as connection:
            connection.execute(self._table.update().where(self._table.c.encounter_id == encounter_id).values(**values))
        with self._db.engine.connect() as connection:
            row = connection.execute(
                self._db.sa.select(self._table).where(self._table.c.encounter_id == encounter_id)
            ).mappings().first()
        if not row:
            raise KeyError("encounter not found")
        return _encounter(row)


class PostgresTimelineRepository:
    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._table = database.tables["timeline_events"]

    def append(
        self,
        principal: Principal,
        *,
        patient_id: str,
        event_type: str,
        encounter_id: str | None = None,
        payload: dict[str, object] | None = None,
        occurred_at: datetime | None = None,
    ) -> TimelineEvent:
        from datetime import timezone
        from uuid import uuid4

        event = TimelineEvent(
            event_id=f"event-{uuid4().hex[:12]}",
            organization_id=principal.organization_id,
            patient_id=patient_id,
            event_type=event_type,
            occurred_at=occurred_at or datetime.now(timezone.utc),
            encounter_id=encounter_id,
            payload=payload or {},
        )
        with self._db.engine.begin() as connection:
            connection.execute(self._table.insert().values(
                event_id=event.event_id,
                organization_id=event.organization_id,
                patient_id=event.patient_id,
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                encounter_id=event.encounter_id,
                payload=dict(event.payload),
            ))
        return event

    def list_for(self, principal: Principal, patient_id: str) -> tuple[TimelineEvent, ...]:
        with self._db.engine.connect() as connection:
            rows = connection.execute(
                self._db.sa.select(self._table).where(
                    self._db.sa.and_(
                        self._table.c.organization_id == principal.organization_id,
                        self._table.c.patient_id == patient_id,
                    )
                ).order_by(self._table.c.occurred_at)
            ).mappings()
            return tuple(_timeline(row) for row in rows)


class PostgresAuditLog:
    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._table = database.tables["audit_entries"]

    def append(self, entry: AuditEntry) -> None:
        with self._db.engine.begin() as connection:
            connection.execute(self._table.insert().values(
                entry_id=entry.entry_id,
                organization_id=entry.organization_id,
                actor_id=entry.actor_id,
                action=entry.action,
                resource_type=entry.resource_type,
                resource_id=entry.resource_id,
                outcome=entry.outcome,
                metadata=dict(entry.metadata),
                occurred_at=entry.occurred_at,
            ))

    def list_for_organization(self, organization_id: str, *, limit: int = 100, action: str | None = None) -> tuple[AuditEntry, ...]:
        clauses = [self._table.c.organization_id == organization_id]
        if action is not None:
            clauses.append(self._table.c.action == action)
        with self._db.engine.connect() as connection:
            rows = connection.execute(
                self._db.sa.select(self._table).where(self._db.sa.and_(*clauses)).order_by(self._table.c.occurred_at.desc()).limit(limit)
            ).mappings()
            return tuple(_audit(row) for row in rows)


class PostgresPrivacyService:
    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._consents = database.tables["privacy_consents"]
        self._requests = database.tables["privacy_requests"]

    def record_consent(self, consent: ConsentRecord) -> None:
        with self._db.engine.begin() as connection:
            connection.execute(self._consents.insert().values(
                consent_id=consent.consent_id, organization_id=consent.organization_id,
                subject_id=consent.subject_id, purpose=consent.purpose,
                policy_version=consent.policy_version, granted=consent.granted,
                recorded_at=consent.recorded_at,
            ))

    def request(self, data_subject_request: DataSubjectRequest) -> None:
        with self._db.engine.begin() as connection:
            connection.execute(self._requests.insert().values(
                request_id=data_subject_request.request_id,
                organization_id=data_subject_request.organization_id,
                subject_id=data_subject_request.subject_id,
                request_type=data_subject_request.request_type,
                status=data_subject_request.status,
                requested_at=data_subject_request.requested_at,
            ))

    def list_consents(self, organization_id: str, subject_id: str) -> tuple[ConsentRecord, ...]:
        with self._db.engine.connect() as connection:
            rows = connection.execute(
                self._db.sa.select(self._consents).where(self._db.sa.and_(
                    self._consents.c.organization_id == organization_id,
                    self._consents.c.subject_id == subject_id,
                )).order_by(self._consents.c.recorded_at.desc())
            ).mappings()
            return tuple(_consent(row) for row in rows)

    def list_requests(self, organization_id: str, subject_id: str | None = None) -> tuple[DataSubjectRequest, ...]:
        clauses = [self._requests.c.organization_id == organization_id]
        if subject_id is not None:
            clauses.append(self._requests.c.subject_id == subject_id)
        with self._db.engine.connect() as connection:
            rows = connection.execute(
                self._db.sa.select(self._requests).where(self._db.sa.and_(*clauses)).order_by(self._requests.c.requested_at.desc())
            ).mappings()
            return tuple(_data_subject_request(row) for row in rows)


class PostgresRecoveryCoordinator:
    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._table = database.tables["recovery_plans"]

    def register(self, plan: RecoveryPlan) -> None:
        with self._db.engine.begin() as connection:
            existing = connection.execute(self._db.sa.select(self._table.c.service).where(self._table.c.service == plan.service)).first()
            values = {
                "service": plan.service, "rto_minutes": plan.rto_minutes,
                "rpo_minutes": plan.rpo_minutes, "dependencies": list(plan.dependencies),
                "last_drill_at": plan.last_drill_at, "last_drill_passed": plan.last_drill_passed,
            }
            if existing:
                connection.execute(self._table.update().where(self._table.c.service == plan.service).values(**values))
            else:
                connection.execute(self._table.insert().values(**values))

    def record_drill(self, service: str, *, passed: bool) -> None:
        with self._db.engine.begin() as connection:
            result = connection.execute(self._table.update().where(self._table.c.service == service).values(
                last_drill_at=datetime.now(timezone.utc), last_drill_passed=passed,
            ))
            if result.rowcount == 0:
                raise KeyError(service)

    def status(self) -> RecoveryStatus:
        with self._db.engine.connect() as connection:
            rows = connection.execute(self._db.sa.select(self._table).order_by(self._table.c.service)).mappings()
            return RecoveryStatus(plans=tuple(_recovery_plan(row) for row in rows))


class PostgresReviewRepository:
    """Persist the existing review projection without changing the Runtime."""

    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._table = database.tables["review_records"]
        self._projection = InMemoryClinicalReviewStore()

    def begin(self, encounter_id: str, patient_id: str) -> None:
        self._projection.begin(encounter_id, patient_id)
        self._persist(encounter_id)

    def record(self, event: Any) -> None:
        self._hydrate(event.stream_id)
        self._projection.record(event)
        self._persist(event.stream_id)

    def complete(self, encounter_id: str, status: str = "completed") -> None:
        self._hydrate(encounter_id)
        self._projection.complete(encounter_id, status)
        self._persist(encounter_id)

    def set_representation(self, encounter_id: str, format_name: str, content: Any) -> None:
        self._hydrate(encounter_id)
        self._projection.set_representation(encounter_id, format_name, content)
        self._persist(encounter_id)

    def save_result(self, encounter_id: str, patient_id: str, result: dict[str, Any]) -> None:
        self._projection.save_result(encounter_id, patient_id, result)
        self._persist(encounter_id)

    def get(self, encounter_id: str) -> dict[str, Any] | None:
        self._hydrate(encounter_id)
        return self._projection.get(encounter_id)

    def list_for(self, patient_id: str | None = None) -> list[dict[str, Any]]:
        with self._db.engine.connect() as connection:
            query = self._db.sa.select(self._table)
            if patient_id is not None:
                query = query.where(self._table.c.patient_id == patient_id)
            rows = connection.execute(query).mappings()
            for row in rows:
                self._projection.restore(row["record"])
        return self._projection.list_for(patient_id)

    def _hydrate(self, encounter_id: str) -> None:
        with self._db.engine.connect() as connection:
            row = connection.execute(
                self._db.sa.select(self._table).where(self._table.c.encounter_id == encounter_id)
            ).mappings().first()
        if row:
            self._projection.restore(row["record"])

    def _persist(self, encounter_id: str) -> None:
        record = self._projection.get(encounter_id)
        if record is None:
            return
        now = datetime.now(timezone.utc)
        with self._db.engine.begin() as connection:
            existing = connection.execute(
                self._db.sa.select(self._table.c.encounter_id).where(self._table.c.encounter_id == encounter_id)
            ).first()
            values = {
                "encounter_id": encounter_id,
                "patient_id": record.get("patient_id"),
                "status": record.get("status", "in_progress"),
                "record": record,
                "updated_at": now,
            }
            if existing:
                connection.execute(self._table.update().where(self._table.c.encounter_id == encounter_id).values(**values))
            else:
                connection.execute(self._table.insert().values(**values))


class PostgresCredentialStore:
    def __init__(self, database: SqlDatabase) -> None:
        self._db = database
        self._table = database.tables["credentials"]

    def register_user(self, credentials: LoginCredentials, principal: Principal) -> None:
        with self._db.engine.begin() as connection:
            connection.execute(self._table.insert().values(
                email=credentials.email.lower(),
                password_hash=InMemoryCredentialStore._hash_password(credentials.password),
                principal=principal.to_claims(),
            ))

    def authenticate_credentials(self, credentials: LoginCredentials) -> Principal:
        with self._db.engine.connect() as connection:
            row = connection.execute(
                self._db.sa.select(self._table).where(self._table.c.email == credentials.email.lower())
            ).mappings().first()
        if not row:
            raise AuthenticationError("invalid credentials")
        expected = InMemoryCredentialStore._hash_password(credentials.password)
        if not _compare_digest(row["password_hash"], expected):
            raise AuthenticationError("invalid credentials")
        return _principal(row["principal"])


def _compare_digest(left: bytes, right: bytes) -> bool:
    import hmac
    return hmac.compare_digest(left, right)


def _patient(row: Any) -> Patient:
    return Patient(row["patient_id"], row["organization_id"], row["full_name"], row["birth_date"], row["active"])


def _workspace(row: Any) -> Workspace:
    return Workspace(row["workspace_id"], row["organization_id"], row["name"], row["slug"])


def _encounter_values(encounter: Encounter) -> dict[str, Any]:
    return {
        "started_at": encounter.started_at,
        "ended_at": encounter.ended_at,
        "patient_joined_at": encounter.patient_joined_at,
        "status": encounter.status,
        "consent_status": encounter.consent_status,
        "camera_ready": encounter.camera_ready,
        "microphone_ready": encounter.microphone_ready,
    }


def _encounter(row: Any) -> Encounter:
    return Encounter(
        encounter_id=row["encounter_id"], organization_id=row["organization_id"],
        workspace_id=row["workspace_id"], patient_id=row["patient_id"],
        professional_id=row["professional_id"], status=row["status"],
        started_at=row["started_at"], ended_at=row["ended_at"],
        patient_joined_at=row["patient_joined_at"], consent_status=row["consent_status"],
        camera_ready=row["camera_ready"], microphone_ready=row["microphone_ready"],
    )


def _timeline(row: Any) -> TimelineEvent:
    return TimelineEvent(
        event_id=row["event_id"], organization_id=row["organization_id"],
        patient_id=row["patient_id"], event_type=row["event_type"],
        occurred_at=row["occurred_at"], encounter_id=row["encounter_id"],
        payload=row["payload"] or {},
    )


def _audit(row: Any) -> AuditEntry:
    return AuditEntry(
        entry_id=row["entry_id"], organization_id=row["organization_id"],
        actor_id=row["actor_id"], action=row["action"], resource_type=row["resource_type"],
        resource_id=row["resource_id"], outcome=row["outcome"],
        metadata=tuple(sorted((row["metadata"] or {}).items())), occurred_at=row["occurred_at"],
    )


def _consent(row: Any) -> ConsentRecord:
    return ConsentRecord(
        consent_id=row["consent_id"], organization_id=row["organization_id"],
        subject_id=row["subject_id"], purpose=row["purpose"],
        policy_version=row["policy_version"], granted=row["granted"],
        recorded_at=row["recorded_at"],
    )


def _data_subject_request(row: Any) -> DataSubjectRequest:
    return DataSubjectRequest(
        request_id=row["request_id"], organization_id=row["organization_id"],
        subject_id=row["subject_id"], request_type=row["request_type"],
        status=row["status"], requested_at=row["requested_at"],
    )


def _recovery_plan(row: Any) -> RecoveryPlan:
    return RecoveryPlan(
        service=row["service"], rto_minutes=row["rto_minutes"],
        rpo_minutes=row["rpo_minutes"], dependencies=tuple(row["dependencies"] or ()),
        last_drill_at=row["last_drill_at"], last_drill_passed=row["last_drill_passed"],
    )


def _principal(claims: dict[str, Any]) -> Principal:
    return Principal(
        user_id=claims["sub"], email=claims["email"], organization_id=claims["organization_id"],
        workspace_ids=tuple(claims.get("workspace_ids", [])), roles=tuple(claims.get("roles", [])),
        permissions=tuple(claims.get("permissions", [])),
    )
