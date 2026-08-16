# Astera Architecture Constitution

**Status:** Normative refactoring gate  
**Scope:** Astera Clinical Runtime, `packages/`, plugin contracts and the
boundary with `astera-live-transcriber`  
**Date:** 2026-08-15

This document defines executable architectural rules for the Astera modular
monolith. It protects boundaries that already exist conceptually; it does not
authorize a new service, a rewrite, or a change to the approved product
architecture.

## 1. Dependency rule

Dependencies point toward policies and contracts. Outer details may depend on
inner policies; inner policies must not depend on delivery mechanisms,
frameworks, vendors or infrastructure.

| Area | May depend on | Must not depend on |
|---|---|---|
| `domain/` | standard library and stable contracts | `application/`, `adapters/`, `infrastructure/`, `presentation/`, vendor SDKs |
| `application/` | `domain/`, inbound/outbound ports and stable contracts | `adapters/`, `infrastructure/`, `presentation/`, concrete infrastructure |
| `adapters/` and `infrastructure/` | `application/`, `domain/`, ports, contracts and vendor SDKs | — |
| `bootstrap/` | every concrete implementation needed to compose the process | business rules owned by the composition root |
| `packages/` | other contract packages and standard library | any `apps/*` module |

The following package graph is normative:

```text
contracts
    ↓
plugin_sdk
    ↓
runtime
```

Here the arrow means “may be depended on”. Therefore:

- `plugin_sdk` may depend on `packages/contracts`;
- Runtime modules may depend on `plugin_sdk` and `packages/contracts`;
- `packages/* → apps/*` is forbidden;
- `plugin_sdk` must never import `apps.runtime`.

## 2. Forbidden application dependencies

Code under `apps/runtime/src/application/` must not import or instantiate:

- `InMemory*` implementations;
- Google ADK or other agent-framework implementations;
- FastAPI, Starlette or WebSocket transport types;
- SQLAlchemy, async database clients or ORM models;
- Redis, NATS, MinIO or Qdrant clients;
- provider HTTP SDKs (`httpx` included when used as a provider detail);
- concrete persistence, messaging, observability or UI adapters.

The application defines or consumes a port. The adapter implements that port.
An in-memory implementation is valid for tests and local development, but it
must be replaceable through the same port and must not leak into application
code.

## 3. Composition root

Only `apps/runtime/src/bootstrap/` may construct the object graph of concrete
adapters. `AsteraKernel` is a facade/orchestrator over dependencies supplied by
bootstrap; it is not a hidden composition root.

Future wiring must follow this shape:

```python
dependencies = AsteraKernelDependencies(
    capability_registry=capability_registry,
    provider_registry=provider_registry,
    plugin_resolver=plugin_resolver,
    event_bus=event_bus,
    agent_runtime=agent_runtime,
)
kernel = AsteraKernel(dependencies)
```

The exact types may evolve, but construction of concrete NATS, Postgres,
Redis, ADK and provider adapters remains in bootstrap or an explicitly owned
composition module called by bootstrap.

## 4. Bounded-context ownership

### `astera-live-transcriber` owns

- microphone/audio capture and buffering;
- VAD and speech providers;
- STT and speech-provider normalization;
- speaker/turn processing related to speech;
- transcript segments and their `partial`, `revised` and `committed` lifecycle;
- transcript provenance and speech telemetry.

### Astera Clinical Runtime owns

- clinical observations and evidence interpretation;
- facts, context, correlation and knowledge;
- clinical reasoning;
- SOAP/FHIR/summary representations;
- clinical review and A2UI clinical projection;
- clinical telemetry and recovery of clinical workflows.

### `packages/contracts` owns

- versioned schemas and event envelopes;
- transcript events consumed by Clinical Runtime;
- evidence contracts;
- compatibility and contract versioning rules.

The two repositories must not import one another. They communicate only
through versioned contracts/events. Clinical Runtime consumes an evidence event
whose provenance may be a transcription; it does not know or depend on a
transcriber implementation.

## 5. Legacy transcription inventory

Before any refactoring of `live_stream.py`, classify existing code as follows.
This inventory is a boundary decision, not a migration instruction.

| Existing concern | Decision | Rationale |
|---|---|---|
| Audio chunks, audio queues and audio ingestion | **REMOVE/MOVE** | Owned by `astera-live-transcriber`; Clinical Runtime consumes events |
| Speech engine invocation and speech adapters | **REMOVE/MOVE** | STT provider ownership belongs to the transcriber repository |
| Transcript lifecycle/state and speech-only metrics | **REMOVE/MOVE** | Must be emitted by the transcriber contract |
| Clinical normalization from committed evidence onward | **KEEP/REIMPLEMENT** | Clinical Runtime owns interpretation of evidence |
| Facts, context, knowledge, reasoning and representations | **KEEP** | Core clinical capability |
| A2UI clinical projection | **KEEP** | Presentation of clinical state belongs to Astera |
| Clinical review projection and persistence port | **KEEP/REIMPLEMENT** | Clinical Runtime owns review; storage must become an adapter |
| Generic event envelope and transcript/evidence schemas | **MOVE** | Shared versioned contracts belong in `packages/contracts` |
| In-memory stream transport | **DEPRECATE/REIMPLEMENT** | Keep as a test adapter; production transport is selected outside application |

Existing code must not be copied into `astera-live-transcriber` merely to
preserve the old path. If the dedicated repository already implements a
capability, the Astera copy is a deprecation/removal candidate.

## 6. Use-case responsibility

An orchestrator/use case may coordinate a workflow, but it must not
simultaneously own infrastructure transport, persistence, UI projection and
the complete clinical rule set. Such code must be decomposed only after the
boundaries above are protected and the ownership inventory is respected.

## 7. Evidence immutability and Knowledge/Research boundaries

Raw Evidence and Canonical Evidence are immutable inputs to the Clinical
Runtime. Knowledge, Research, Correlation and Representation may create
derived results and projections, but they must not overwrite source evidence,
transcript identity, segment revision, original text, timestamps or
provenance.

The application depends on provider-neutral ports:

```text
Clinical Runtime
      ├── KnowledgePort
      └── ResearchPort
```

Knowledge answers what is known about a clinical concept. Research retrieves
external findings for a clinical question. MedCAT, DEEPMED Search, PubMed,
HTTP clients and vendor SDKs are adapters, not application dependencies. The
Runtime must never construct or import them directly.

KnowledgeResult, ResearchResult, Correlation and Clinical State are derived
outputs. They may carry evidence identifiers and provenance references, but
they are not alternate mutable representations of Raw or Canonical Evidence.

Terminology linking is a separate boundary from Knowledge enrichment:

```text
Canonical Evidence → Clinical Normalization → TerminologyPort
                                           → TerminologyResult
```

Clinical context construction is also an independent provider-neutral port:

```text
Canonical Mention → ClinicalContextPort → ClinicalContextResult
Clinical Facts    → ClinicalContextBuilderPort → ClinicalContext
```

QuickUMLS and MedCAT are possible `TerminologyPort` adapters. medspaCy and
NIEDE language rules are possible `ClinicalContextPort` adapters. None of
these tools may be imported by `application/` or `domain/`, and no benchmark
choice is implied by the existence of the ports.

## 8. Enforcement

`tests/architecture/` is the executable form of this Constitution. Architecture
fitness tests are intentionally separate from behavioral tests and may fail
while known debt is being removed. They must not be weakened with exceptions
that merely make CI green.

Any intentional exception requires an ADR or an update to the authoritative
Astera Flow before the exception is added to the tests.
