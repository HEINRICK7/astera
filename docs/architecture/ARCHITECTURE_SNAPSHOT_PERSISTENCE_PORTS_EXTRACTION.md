# Architecture Snapshot — Persistence Ports Extraction

Status: completed.

This milestone extracted persistence/state boundaries without connecting
PostgreSQL, Redis, NATS or MinIO.

## Dependency direction

```text
Application
    ↓
Persistence/state ports
    ↑
In-memory adapters
    ↑
Bootstrap composition root
```

## Extracted ports

- `PatientRepositoryPort`
- `EncounterRepositoryPort`
- `WorkspaceRepositoryPort`
- `TimelineRepositoryPort`
- `AuthenticationPort`
- `CredentialStorePort`
- `SessionStorePort`
- `TokenIssuerPort`
- `AuditLogPort`
- `ReviewRepositoryPort`
- `SessionStatePort`
- `ClinicalEvidenceStorePort`
- `EvidenceObjectStorePort`

## Concrete development adapters

- `InMemoryPatientRepository`
- `InMemoryEncounterRepository`
- `InMemoryWorkspaceRepository`
- `InMemoryTimelineRepository`
- `InMemoryAuthenticationService`
- `InMemoryClinicalReviewStore`
- existing audit, privacy, backup, recovery, observability, performance and
  streaming in-memory adapters.

The old directory/service names remain only as compatibility aliases. They are
not used as application abstractions.

## Boundary proof

- Application code does not import adapters.
- Application code does not import `PatientDirectory`, `EncounterDirectory`,
  `WorkspaceDirectory`, `TimelineDirectory`, `AuthService` or
  `ClinicalReviewResultStore`.
- `LiveClinicalPipeline` requires `ReviewRepositoryPort` explicitly.
- Bootstrap is the only place that selects concrete development adapters.

## Validation

- Behavioral tests: 123 passed.
- Architecture tests: 8 passed.
- Full validation suite: 131 passed.
- `git diff --check`: passed.

## Deliberately deferred

The authentication facade now composes `InMemoryCredentialStore`,
`InMemorySessionStore` and `JwtTokenIssuer`. Production identity, session and
token adapters remain deferred without changing application callers.

Production adapters, schemas, transaction boundaries, Redis TTL policy,
object-store retention and restart/recovery tests belong to the next milestone.
