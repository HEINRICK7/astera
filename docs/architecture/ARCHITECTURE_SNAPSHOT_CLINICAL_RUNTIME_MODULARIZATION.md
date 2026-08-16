# Architecture Snapshot — Clinical Runtime Modularization

Status: Clinical Runtime modularization completed inside the monorepo;
physical repository split is intentionally deferred.

## Internal Clinical Runtime graph

```text
EvidenceIngressPort
        ↓
ingestion
        ↓
observations → facts
        ↓        ↓
      context / correlation
              ↓
       knowledge → research
              ↓
       Clinical State
              ↓
 representation → projections
```

The modules live under `apps/runtime/src/application/clinical/modules`. They
are in-process bounded contexts, not public packages. Existing files such as
`normalization.py`, `knowledge_layer.py` and `presentation_composer.py` remain
compatibility implementations behind the new module seams; their rules were
not duplicated or moved into `packages/contracts`.

## Boundary rules

- ingestion owns canonical event-to-runtime evidence conversion;
- observations owns normalization and mention lifecycle;
- facts owns extraction of clinical facts;
- context owns the evolving clinical context projection;
- correlation/knowledge owns fact relationships and clinical state;
- research/reasoning is optional deep work and does not control the stream;
- representation consumes clinical projections, not transcript transport;
- projections translate state into A2UI/clinician-facing output and contain no
  clinical inference.

The public `live_stream.py` is now a 90-line compatibility facade. It delegates
to an 86-line `ClinicalOrchestrator`, which delegates session mechanics to
`RuntimeSession`. Runtime-only concerns (queues, lifecycle, dispatch, ordered
publication, review projection and cleanup) stay outside the semantic
processing module. `processing.py` owns fast and deep clinical processing.

The module fitness suite checks that the graph is acyclic, the public facade
cannot grow into a pipeline again, and UI/transcription dependencies do not
leak across the declared boundaries.

## Validation

- behavioral suite remains green;
- architecture fitness expanded from 8 to 13 passing tests;
- canonical clinical runner remains green;
- no legacy speech ownership was reintroduced.

The next milestone is Knowledge & Research Boundary: isolate terminology,
MedCAT and DEEPMED Search behind research/knowledge ports without making them
part of the primary clinical flow.
