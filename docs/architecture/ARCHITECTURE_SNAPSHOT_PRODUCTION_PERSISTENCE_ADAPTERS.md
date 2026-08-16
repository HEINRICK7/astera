# Architecture Snapshot — Production Persistence Adapters

Status: implemented and integration-validated.

## Runtime selection

```text
development/test
    Application → Ports → InMemory adapters

production
    Application → Ports → PostgreSQL / Redis / MinIO adapters
```

The selection happens in the bootstrap from `ASTERA_ENVIRONMENT`. Application
and Clinical Runtime code do not import SQLAlchemy, Redis or MinIO.

## Implemented adapters

PostgreSQL/SQLAlchemy:

- patients and encounters;
- workspaces and timeline events;
- audit log;
- clinical review projection;
- privacy records;
- recovery plans;
- credential records.

Redis:

- shared clinical session state with TTL;
- consume-once refresh-token sessions.

MinIO/S3-compatible object storage:

- immutable raw evidence objects;
- backup payloads, with PostgreSQL manifests and SHA-256 verification.

## Transaction and lifecycle decisions

- each repository mutation uses a database transaction;
- PostgreSQL is the system of record for durable relational state;
- review remains a projection and can be rebuilt from canonical events;
- Redis state is explicitly TTL-bound and not a clinical record;
- raw evidence payloads are kept outside PostgreSQL, while provenance and
  integrity metadata remain associated with the object/manifest.

## Validation

- local SQL restart/round-trip test passed;
- real PostgreSQL restart/round-trip test passed;
- real Redis shared-state and refresh-session test passed;
- real MinIO object and backup checksum test passed;
- production bootstrap selected PostgreSQL/Redis/MinIO adapters successfully;
- behavioral + architecture suite: 134 passed;
- architecture fitness: 8/8 passed.

The next milestone is Production Bootstrap & Recovery Hardening: migrations,
health checks, retry/reconnect policy, startup/shutdown failure handling,
backups and recovery drills.
