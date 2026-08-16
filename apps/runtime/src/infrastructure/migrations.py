"""Small, explicit migration runner for Runtime persistence.

The first migration deliberately reuses the SQLAlchemy metadata because the
production adapters already own the canonical table definitions.  The schema
change is still recorded in an append-only, ordered table so startup is
idempotent and future changes have a place to land without silently relying on
``create_all``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class Migration:
    version: str
    description: str
    apply: Callable[[Any], None]


class MigrationRunner:
    """Apply ordered migrations exactly once per database."""

    def __init__(self, engine: Any, metadata: Any, *, migrations: tuple[Migration, ...]) -> None:
        self._engine = engine
        self._metadata = metadata
        self._migrations = tuple(sorted(migrations, key=lambda migration: migration.version))

    def upgrade(self) -> tuple[str, ...]:
        from sqlalchemy import Column, DateTime, MetaData, String, Table, func, select, text

        migration_metadata = MetaData()
        schema_migrations = Table(
            "schema_migrations",
            migration_metadata,
            Column("version", String(64), primary_key=True),
            Column("description", String(255), nullable=False),
            Column("applied_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        )
        with self._engine.begin() as connection:
            # Multiple Runtime replicas can boot simultaneously. PostgreSQL's
            # transaction advisory lock serializes migration ownership without
            # introducing an application-level coordinator. SQLite keeps its
            # normal database lock for local/test usage.
            if self._engine.dialect.name == "postgresql":
                connection.execute(text("SELECT pg_advisory_xact_lock(hashtext('astera.schema_migrations'))"))
            migration_metadata.create_all(connection, tables=[schema_migrations], checkfirst=True)
            applied = set(connection.execute(select(schema_migrations.c.version)).scalars())

            newly_applied: list[str] = []
            for migration in self._migrations:
                if migration.version in applied:
                    continue
                migration.apply(connection)
                connection.execute(
                    schema_migrations.insert().values(
                        version=migration.version,
                        description=migration.description,
                    )
                )
                newly_applied.append(migration.version)
        return tuple(newly_applied)

    def applied_versions(self) -> tuple[str, ...]:
        from sqlalchemy import MetaData, Table, select

        metadata = MetaData()
        schema_migrations = Table(
            "schema_migrations",
            metadata,
            autoload_with=self._engine,
        )
        with self._engine.connect() as connection:
            return tuple(
                connection.execute(select(schema_migrations.c.version).order_by(schema_migrations.c.version)).scalars()
            )


def initial_metadata_migration(metadata: Any) -> Migration:
    """Return the baseline migration for all current durable tables."""

    def apply(connection: Any) -> None:
        metadata.create_all(connection)

    return Migration(
        version="001",
        description="initial durable Runtime persistence schema",
        apply=apply,
    )
