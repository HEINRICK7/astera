# Persistence Boundary — Inventory & Ports

Status: inventory complete; production adapters connected by environment.

This milestone classifies lifecycle and ownership before choosing PostgreSQL,
Redis, NATS or object storage. `InMemory` is an adapter choice, not a domain
model. Names such as `PatientDirectory` and `AuthService` are currently
concrete development implementations; they are not ports merely because the
name does not contain `InMemory`.

## Classification by behavior

| Component | Evidence in current implementation | Lifecycle decision | Owner |
| --- | --- | --- | --- |
| `InMemoryPatientRepository` (formerly `PatientDirectory`) | process-local `dict[str, Patient]`; lost on restart | durable | Patient/identity boundary |
| `InMemoryEncounterRepository` (formerly `EncounterDirectory`) | process-local `dict[str, Encounter]`; lifecycle mutations are local | durable | Encounter boundary |
| `InMemoryWorkspaceRepository` (formerly `WorkspaceDirectory`) | process-local membership records | durable, unless rebuilt from identity provider | Workspace/identity boundary |
| `InMemoryTimelineRepository` (formerly `TimelineDirectory`) | process-local append-only `list[TimelineEvent]` | durable history; publish integration events separately | Timeline boundary |
| `InMemoryAuthenticationService` users | process-local credential map | durable credentials/identity | Authentication boundary |
| `InMemoryAuthenticationService` refresh tokens | process-local revocable token map | ephemeral/revocable session state | Session/auth boundary |
| `InMemoryClinicalReviewStore` (formerly `ClinicalReviewResultStore`) | process-local review projection updated from runtime events | durable review/audit view, rebuildable from canonical events | Clinical review boundary |
| `ClinicalTranscriptState` | active segments and partials for one session | ephemeral/session; Redis only if resumability is required | Clinical session boundary |
| `EvidenceStore` | in-process facts, lifecycle indexes and history | derived/rebuildable projection | Clinical evidence projection |
| `InMemoryStreamBrokerAdapter` | process-local event delivery/subscriptions | event/ephemeral | Streaming/integration boundary |
| raw evidence objects | not yet persisted by the Runtime | durable blob with provenance | Evidence object boundary |

This is a behavior/lifecycle classification, not a rename exercise. The
current concrete implementations remain useful for tests and local bootstrap;
the application-facing code receives explicit ports instead of inheriting from
or pretending that those implementations are abstractions.

## Stateful process components that are not system-of-record stores

These components were included in the inventory because they retain mutable
state, but that state is coordination, cache, projection or process
configuration rather than a durable record.

| Component | Current state | Lifecycle | Shared between replicas? | Storage/port decision |
| --- | --- | --- | --- | --- |
| `ContextManager` | `_sessions: dict` of active `ContextScope` objects | ephemeral/session | yes if a session can move between replicas | Redis or memory with sticky ownership; `SessionStatePort` |
| `ClinicalTranscriptState` / `ConversationMemory` | active partials and committed segment projection | ephemeral/session | yes only for resumability | memory first; Redis later; `SessionStatePort` |
| `QueueEvidenceIngress` | `asyncio.Queue` of canonical events | event/ephemeral | no; queue ownership is local | message broker when cross-process delivery is required; `EvidenceIngressPort` |
| `LiveClinicalPipeline._active_evidence_ingresses` | active stream-to-ingress map | ephemeral coordination | no | process memory; no durable port |
| `ClinicalA2UIProjector` | current A2UI nodes/workspace delta | derived/session projection | no; rebuild from clinical projection | memory; no persistence port |
| `ClinicalKnowledgeLayer` / `EvidenceStore` | facts, lifecycle indexes, timeline and history | derived/rebuildable | not as source of truth | rebuild from canonical evidence; `ClinicalEvidenceStorePort` only if materialization is needed |
| `MentionRegistry` | normalized mention identity and observation counts | derived/rebuildable | no | rebuild from evidence; no durable port in this milestone |
| `ClinicalPresentationComposer` | object lifecycle/age/focus/archive sets | derived/session projection | no | memory; no persistence port |
| `CapabilityRegistry` | registered capability descriptors | process configuration | loaded per process | manifests/config; no database port |
| `ProviderRegistry` | provider metadata and health status | process configuration/health cache | no, unless a control plane is introduced | bootstrap/control plane; no clinical persistence port |
| `PluginResolver` / `PluginRegistry` | live plugin bindings and lifecycle records | process runtime | no | bootstrap/plugin control plane; no clinical persistence port |
| Google ADK `InMemorySessionService` | vendor agent sessions | ephemeral/session | vendor/runtime dependent | adapter-owned; `AgentRuntimePort`, not clinical persistence |
| OpenTelemetry counters/instrument handles | process-local instrumentation objects | derived/ephemeral telemetry | no | telemetry backend through existing observability port |

The rule is deliberate: mutable state does not automatically imply a
repository. A repository is required when the state represents a business or
operational record whose lifecycle must outlive a process. A projection or
coordination structure gets a rebuild, cache or session decision instead.

## Stateful components excluded from persistence

The deterministic NLP, OCR, vision, reasoning, embedding and evaluation
implementations hold only immutable provider configuration or algorithmic
parameters. `GrokClient`, NATS connection objects and HTTP/vendor clients hold
resource lifecycle state, not Astera records. They remain adapters/providers,
not persistence candidates.

## Lifecycle classification

| Current implementation/state | Current location | Lifecycle | Target ownership | Port status |
| --- | --- | --- | --- | --- |
| `InMemoryPatientRepository` | `packages/patient_sdk` | durable | PostgreSQL | `PatientRepositoryPort` created |
| `InMemoryEncounterRepository` | `packages/encounter_sdk` | durable | PostgreSQL | `EncounterRepositoryPort` created |
| `InMemoryWorkspaceRepository` | `packages/workspace_sdk` | durable | PostgreSQL | `WorkspaceRepositoryPort` created |
| `InMemoryTimelineRepository` | `packages/timeline_sdk` | durable/event projection | PostgreSQL + event publication | `TimelineRepositoryPort` created |
| `InMemoryAuthenticationService` (formerly `AuthService`) users | `packages/auth_sdk` | durable | PostgreSQL/identity provider | `AuthenticationPort` facade plus credential/session/token ports created |
| `InMemoryAuthenticationService` refresh tokens | `packages/auth_sdk` | ephemeral/revocable | Redis or identity provider | `SessionStorePort` identified; adapter remains composite |
| `InMemoryAuditLog` | `packages/audit_sdk` | durable append-only | PostgreSQL/event store | existing `AuditPort`; app facade created |
| `InMemoryPrivacyService` | `packages/privacy_sdk` | durable/legal | PostgreSQL | existing `PrivacyPort` |
| `InMemoryClinicalReviewStore` | `apps/runtime/src/adapters/persistence` | durable projection | PostgreSQL, rebuildable from events | `ReviewRepositoryPort` created |
| `EvidenceStore` | Runtime application | derived projection | rebuild from canonical evidence/events | `ClinicalEvidenceStorePort` created; persistence not required by default |
| `ClinicalTranscriptState` | Runtime application | ephemeral session state | memory/Redis if resumability is required | `SessionStatePort` created |
| `QueueEvidenceIngress` | Runtime application | ephemeral queue | process memory/message transport | inbound port already exists |
| `InMemoryStreamBrokerAdapter` | Runtime adapter | event delivery/ephemeral | NATS for integration; memory for tests | existing `StreamBrokerPort` |
| `InMemoryBackupStore` | `packages/backup_sdk` | durable blob | MinIO/object storage | existing `BackupPort` |
| `InMemoryRecoveryCoordinator` | `packages/disaster_recovery_sdk` | durable operational config | PostgreSQL/config store | existing `RecoveryPort` |
| `InMemoryOperationalObservability` | `packages/observability_sdk` | derived/ephemeral telemetry | OpenTelemetry backend | existing port |
| `InMemoryPerformanceMonitor` | `packages/performance_sdk` | derived/ephemeral telemetry | metrics backend | existing `PerformancePort` |
| `InMemoryFhirGateway` | `packages/fhir_sdk` | external/derived integration | FHIR server | existing `FhirGateway`; not a system of record |
| `InMemoryKnowledgeStore` | `packages/medical_knowledge_sdk` | durable reference data | versioned knowledge store | existing `KnowledgeStore`; outside current product write path |
| `InMemoryReleaseManager` | `packages/release_sdk` | durable release metadata | deployment database/control plane | outside clinical runtime path |

`InMemoryFhirGateway`, `InMemoryKnowledgeStore` and
`InMemoryReleaseManager` are not automatically database tables in Astera:
they are external, reference-data or control-plane boundaries and need their
own ownership decision.

## Existing port inventory

Already available in package/runtime boundaries:

- `StreamBrokerPort` — event delivery;
- `BackupPort` — backup blobs;
- `PrivacyPort` — consent and data-subject workflows;
- `RecoveryPort` — recovery plans/status;
- `AuditPort`/`AuditLogPort` — append-only audit;
- `OperationalObservabilityPort` and `PerformancePort` — telemetry;
- `FhirGateway`, `KnowledgeStore` and other capability protocols — external or
  derived integrations.

Created in this milestone under
[`persistence.py`](/home/carlos-henrique/Documentos/workspace/astera/apps/runtime/src/ports/outbound/persistence.py):

- `AuthenticationPort` — authentication facade, not a repository;
- `CredentialStorePort`, `SessionStorePort` and `TokenIssuerPort` — separate
  responsibilities present inside the current authentication adapter;
- `PatientRepositoryPort`;
- `EncounterRepositoryPort`;
- `WorkspaceRepositoryPort`;
- `TimelineRepositoryPort`;
- `AuditLogPort`;
- `ReviewRepositoryPort`;
- `ClinicalEvidenceStorePort`;
- `EvidenceObjectStorePort` — raw evidence/blob boundary, separate from the
  derived clinical evidence projection;
- `SessionStatePort`.

The HTTP and dashboard application-facing code now depends on these ports,
while the development directories remain concrete composition-root adapters.

Authentication is intentionally tracked as a facade because the public
authentication API combines four responsibilities: durable credentials, token
issuance, refresh-token session state and access-token verification. The
development adapter now composes `InMemoryCredentialStore`,
`InMemorySessionStore` and `JwtTokenIssuer` behind that facade; production
identity/session adapters remain deferred.

## Decisions deferred to the next milestone

Production storage is now connected behind the ports. The following still
require explicit hardening before this boundary is considered operationally
complete:

1. PostgreSQL schema and transaction boundaries for patients, encounters,
   review and audit;
2. Redis resumability policy for active clinical sessions;
3. NATS event subjects, delivery semantics and idempotency keys;
4. MinIO object keys, retention, encryption and provenance linkage;
5. replay/rebuild rules for evidence, knowledge and review projections;
6. restart, recovery and migration tests.

## Current boundary status

```text
Application/Domain
        ↓ ports
Bootstrap composition root
        ↓ current development adapters
InMemory / deterministic implementations
```

The application no longer needs to know whether the next adapter is
PostgreSQL, Redis, NATS or MinIO. `LiveClinicalPipeline` now requires its
`ReviewRepositoryPort`; the Runtime supplies `InMemoryClinicalReviewStore`
from bootstrap/tests. This milestone intentionally stops before production
storage wiring.
