# Architecture Snapshot — PostgreSQL Recovery Drill

Status: completed on 2026-08-15 in the Docker-backed local production stack.

## Recovery boundary

```text
PostgreSQL
    ↓ pg_dump --format=custom
backup artifact
    ↓ payload in MinIO + manifest/checksum in PostgreSQL
pg_restore into a fresh database
    ↓
restored PostgreSQL
    ↓ migrations/readiness
Astera Runtime
```

The recovery operator lives in the persistence adapter boundary. Application
and Domain do not import `pg_dump`, `pg_restore`, SQLAlchemy, MinIO or Docker.
The bootstrap selects the binaries and timeout through infrastructure settings.

## Guarantees exercised

- the dump is stored as a traceable `postgresql.logical` backup artifact;
- the manifest records size and SHA-256 checksum;
- restore reads the custom-format payload through standard input, so the
  operator does not require a host/container shared temporary directory;
- restore targets a uniquely named empty PostgreSQL database;
- patients, encounters, audit entries and review projection were recovered;
- the restored database retained migration version `001`;
- the restored database passed the persistence health check;
- the Runtime started successfully against the restored database and reported
  PostgreSQL, Redis, MinIO and NATS ready;
- the temporary recovery database was removed after the drill.

## Observed recovery measurements

The opt-in integration test `test_postgres_recovery_integration.py` measured:

| Measurement | Observed |
|---|---:|
| `pg_dump` | 0.294 s |
| `pg_restore` | 1.133 s |
| dump + restore window | 1.427 s |

These are observations from the local Docker environment on the drill date,
not production SLOs. The drill demonstrated snapshot-level RPO: the critical
records present at dump time were recovered with no data loss in the restored
database. A time-based RPO still depends on backup scheduling, which is an
operational deployment decision.

## Reproduction

The real drill is intentionally opt-in because it requires the local services:

```bash
ASTERA_RUN_REAL_RECOVERY_DRILL=1 \
  .venv/bin/python -m pytest -q \
  apps/runtime/tests/test_postgres_recovery_integration.py -s
```

The test creates and drops only its uniquely named recovery database. It never
drops or resets the source database.

## Exit criteria

- automated logical dump: complete;
- traceable backup artifact and checksum: complete;
- restore into an empty database: complete;
- critical-record validation: complete;
- Runtime startup after restore: complete;
- migration consistency: complete;
- Application/Domain infrastructure isolation: preserved;
- behavioral and architecture suites: validated separately in the full gate.

The next milestone is Knowledge & Research Boundary.
