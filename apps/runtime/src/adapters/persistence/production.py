"""Production persistence composition for the Runtime bootstrap."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib

from packages.auth_sdk import AuthTokens, AuthorizationError, LoginCredentials, Principal
from packages.backup_sdk import BackupArtifact
from packages.backup_sdk.in_memory import BackupIntegrityError

from apps.runtime.src.infrastructure.settings import AsteraSettings
from apps.runtime.src.ports.outbound.persistence import (
    AuthenticationPort,
    CredentialStorePort,
    SessionStorePort,
    TokenIssuerPort,
)

from .minio import MinioEvidenceObjectStore
from .redis import RedisClientFactory, RedisRefreshSessionStore, RedisSessionStateAdapter
from .sqlalchemy import (
    PostgresAuditLog,
    PostgresPrivacyService,
    PostgresRecoveryCoordinator,
    PostgresCredentialStore,
    PostgresEncounterRepository,
    PostgresPatientRepository,
    PostgresReviewRepository,
    PostgresTimelineRepository,
    PostgresWorkspaceRepository,
    SqlDatabase,
)
from .recovery import PostgresLogicalBackup
from packages.auth_sdk import JwtTokenIssuer


class ProductionAuthenticationService(AuthenticationPort):
    """Authentication facade composed from independent production ports."""

    def __init__(
        self,
        *,
        credentials: CredentialStorePort,
        sessions: SessionStorePort,
        tokens: TokenIssuerPort,
    ) -> None:
        self._credentials = credentials
        self._sessions = sessions
        self._tokens = tokens

    def register_user(self, credentials: LoginCredentials, principal: Principal) -> None:
        self._credentials.register_user(credentials, principal)

    def login(self, credentials: LoginCredentials) -> AuthTokens:
        principal = self._credentials.authenticate_credentials(credentials)
        tokens = self._tokens.issue(principal)
        self._sessions.save(tokens.refresh_token, principal)
        return tokens

    def refresh(self, refresh_token: str) -> AuthTokens:
        principal = self._sessions.consume(refresh_token)
        if principal is None:
            from packages.auth_sdk import AuthenticationError
            raise AuthenticationError("invalid refresh token")
        tokens = self._tokens.issue(principal)
        self._sessions.save(tokens.refresh_token, principal)
        return tokens

    def authenticate(self, access_token: str) -> Principal:
        return self._tokens.verify(access_token)

    def require_permission(self, principal: Principal, permission: str) -> None:
        if permission not in principal.permissions:
            raise AuthorizationError(f"permission required: {permission}")


class PostgresBackupStore:
    """Durable backup manifest in PostgreSQL and payload in object storage."""

    def __init__(self, database: SqlDatabase, objects: MinioEvidenceObjectStore) -> None:
        self._db = database
        self._objects = objects
        self._table = database.tables["backup_artifacts"]

    def create_backup(self, source: str, content: bytes) -> BackupArtifact:
        payload = bytes(content)
        artifact = BackupArtifact.create(
            source=source,
            size_bytes=len(payload),
            checksum_sha256=hashlib.sha256(payload).hexdigest(),
        )
        object_key = f"backups/{artifact.backup_id}"
        self._objects.put(
            object_key,
            payload,
            content_type="application/octet-stream",
            metadata={"source": source, "checksum-sha256": artifact.checksum_sha256},
        )
        with self._db.engine.begin() as connection:
            connection.execute(self._table.insert().values(
                backup_id=artifact.backup_id, source=artifact.source,
                size_bytes=artifact.size_bytes, checksum_sha256=artifact.checksum_sha256,
                status=artifact.status, created_at=artifact.created_at, object_key=object_key,
            ))
        return artifact

    def list_backups(self) -> tuple[BackupArtifact, ...]:
        with self._db.engine.connect() as connection:
            rows = connection.execute(self._db.sa.select(self._table).order_by(self._table.c.created_at.desc())).mappings()
            return tuple(_backup(row) for row in rows)

    def restore(self, backup_id: str) -> bytes:
        with self._db.engine.connect() as connection:
            row = connection.execute(self._db.sa.select(self._table).where(self._table.c.backup_id == backup_id)).mappings().first()
        if not row:
            raise KeyError(backup_id)
        payload = self._objects.get(row["object_key"])
        if payload is None or hashlib.sha256(payload).hexdigest() != row["checksum_sha256"]:
            raise BackupIntegrityError(f"backup integrity check failed: {backup_id}")
        return payload


def _backup(row: object) -> BackupArtifact:
    return BackupArtifact(
        backup_id=row["backup_id"], source=row["source"], size_bytes=row["size_bytes"],
        checksum_sha256=row["checksum_sha256"], status=row["status"], created_at=row["created_at"],
    )


@dataclass(slots=True)
class ProductionPersistenceAdapters:
    database: SqlDatabase
    auth: ProductionAuthenticationService
    patients: PostgresPatientRepository
    encounters: PostgresEncounterRepository
    workspaces: PostgresWorkspaceRepository
    timeline: PostgresTimelineRepository
    audit: PostgresAuditLog
    review: PostgresReviewRepository
    privacy: PostgresPrivacyService
    backups: PostgresBackupStore
    logical_backup: PostgresLogicalBackup
    recovery: PostgresRecoveryCoordinator
    session_state: RedisSessionStateAdapter
    evidence_objects: MinioEvidenceObjectStore
    redis_client: object

    def close(self) -> None:
        self.database.close()
        close = getattr(self.redis_client, "close", None)
        if close is not None:
            close()

    def health_check(self) -> dict[str, bool]:
        """Check every production persistence dependency without app imports."""
        self.database.health_check()
        self.session_state.health_check()
        self.evidence_objects.health_check()
        return {"postgres": True, "redis": True, "minio": True}


def build_production_persistence(settings: AsteraSettings) -> ProductionPersistenceAdapters:
    database = SqlDatabase(settings.postgres_url)
    redis_client = RedisClientFactory.create(settings.redis_url)
    refresh_sessions = RedisRefreshSessionStore(
        redis_client,
        ttl_seconds=settings.auth_access_ttl_seconds * 4,
    )
    auth = ProductionAuthenticationService(
        credentials=PostgresCredentialStore(database),
        sessions=refresh_sessions,
        tokens=JwtTokenIssuer(
            secret=settings.auth_secret,
            access_ttl_seconds=settings.auth_access_ttl_seconds,
        ),
    )
    evidence_objects = MinioEvidenceObjectStore(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        bucket=settings.minio_bucket,
        secure=settings.minio_secure,
    )
    backups = PostgresBackupStore(database, evidence_objects)
    return ProductionPersistenceAdapters(
        database=database,
        auth=auth,
        patients=PostgresPatientRepository(database),
        encounters=PostgresEncounterRepository(database),
        workspaces=PostgresWorkspaceRepository(database),
        timeline=PostgresTimelineRepository(database),
        audit=PostgresAuditLog(database),
        review=PostgresReviewRepository(database),
        privacy=PostgresPrivacyService(database),
        backups=backups,
        logical_backup=PostgresLogicalBackup(
            backups=backups,
            source_url=database.url,
            dump_binary=settings.postgres_dump_binary,
            restore_binary=settings.postgres_restore_binary,
            timeout_seconds=settings.postgres_backup_timeout_seconds,
        ),
        recovery=PostgresRecoveryCoordinator(database),
        session_state=RedisSessionStateAdapter(
            redis_client,
            ttl_seconds=settings.redis_session_ttl_seconds,
        ),
        evidence_objects=evidence_objects,
        redis_client=redis_client,
    )
