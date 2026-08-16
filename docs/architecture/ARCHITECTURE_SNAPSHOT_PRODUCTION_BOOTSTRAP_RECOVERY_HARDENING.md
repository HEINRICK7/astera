# Architecture Snapshot — Production Bootstrap & Recovery Hardening

Status: implemented for the Runtime bootstrap and persistence boundary.

## Startup ownership

```text
bootstrap
    ├── constructs production adapters
    ├── runs versioned migrations
    ├── checks critical dependencies with bounded retry
    ├── starts the Kernel
    └── closes resources in reverse order
```

Application and Domain still receive ports. They do not import SQLAlchemy,
Redis, MinIO or NATS and do not contain reconnect policy.

## Migrations

`SqlDatabase` runs `MigrationRunner` before exposing repositories. The first
baseline is recorded in `schema_migrations` as version `001`; applying the
same database again is a no-op. Future schema changes must add a new ordered
migration instead of restoring an unversioned `metadata.create_all()` call.

## Readiness and failure behavior

- `/health` and `/live` remain process liveness probes;
- `/ready` requires the Kernel plus NATS and, in production, PostgreSQL,
  Redis and MinIO;
- critical production checks retry with bounded exponential backoff;
- NATS has bounded startup retries and client reconnect settings;
- startup fails explicitly when a critical dependency remains unavailable;
- shutdown drains the Kernel and then closes production persistence resources.

## Recovery guarantees currently covered

- durable relational state survives adapter/process restart;
- Redis session state is shared and TTL-bound;
- refresh sessions are consumed once;
- raw evidence and backup payloads preserve SHA-256 integrity;
- migration application is idempotent;
- dependency startup and reverse-order shutdown have automated tests.

The PostgreSQL logical dump/restore drill is now covered separately by
`ARCHITECTURE_SNAPSHOT_POSTGRES_RECOVERY_DRILL.md`. This snapshot retains the
bootstrap and dependency-hardening decisions; the drill snapshot records the
database recovery evidence and measured timings.

## Validation

- behavioral + infrastructure tests: see the current CI gate;
- architecture fitness: see the current CI gate;
- `git diff --check`: clean;
- Docker-backed PostgreSQL, Redis and MinIO integration remains part of the
  production validation procedure.

The next milestone is LiveClinicalPipeline Decomposition.
