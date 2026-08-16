# Knowledge & Research Boundary Inventory

Status: architectural inventory only. No MedCAT, DEEPMED Search, PubMed, HTTP
provider or new external model is integrated by this milestone.

## Current implementation map

| Area | Current implementation | Actual responsibility today | Boundary decision |
|---|---|---|---|
| `modules/knowledge.py` | `ClinicalKnowledgeModule` | Facade over `ClinicalCorrelationModule`; applies facts to the internal clinical projection | Keep as clinical projection facade for now; do not call it external Knowledge |
| `modules/correlation.py` | `ClinicalCorrelationModule` + `ClinicalKnowledgeLayer` | Stateful deduplication, lifecycle, graph, cards, timeline and history derived from `ClinicalFactsBatch` | Keep as derived Correlation/Clinical State; it must not mutate canonical evidence |
| `knowledge_layer.py` | `ClinicalKnowledgeLayer` + `KnowledgeProjection` | Builds graph and reviewable cards from the internal `EvidenceStore` | Derived projection; not a terminology provider |
| `evidence_store.py` | `EvidenceStore` | Maintains an in-process fact projection and history | Derived Runtime state; source facts remain immutable inputs |
| `modules/research.py` | `ClinicalResearchModule` | Delegates `ClinicalContext` to `ClinicalReasoner` | Current reasoning boundary, not external Research; preserve until a separate cutover |
| `reasoning_sdk` | `ClinicalReasoner` + deterministic/Grok implementations | Hypotheses, gaps and reasoning result from clinical context | Reasoning provider; do not rename it into Research implicitly |
| `modules/normalization.py` | `ClinicalNormalizationLayer` | Rule-based mention extraction, normalization and fact candidates | Clinical interpretation of evidence; no vendor knowledge dependency today |
| `modules/processing.py` | `ClinicalProcessingModule` | Coordinates normalization → facts → internal projection and context → reasoning → representation | Consumer/orchestrator; later injects `KnowledgePort` and `ResearchPort` explicitly |
| `runtime_session.py` / `orchestrator.py` | Runtime coordination | Owns session execution and supplies clinical modules | Composition/use-case boundary; no vendor construction |
| `representation.py` / `projections.py` | Clinical output adapters | Converts derived clinical state to SOAP/FHIR/A2UI projections | Read derived state only; never rewrite raw/canonical evidence |

## Existing provider-neutral capabilities

The repository already contains provider-neutral foundations, but they are not
the same as the Clinical Runtime boundary:

- `packages/terminology_sdk` defines `TerminologyService` and terminology DTOs;
- `packages/medical_knowledge_sdk` defines document, query, source and evidence
  contracts plus a local retrieval service;
- `packages/knowledge_pipeline_sdk` defines a consolidation engine for a
  knowledge record;
- `packages/correlation_sdk` defines a correlation engine contract, while the
  current Runtime path still uses its own internal `ClinicalKnowledgeLayer`;
- `packages/reasoning_sdk` defines the currently consumed reasoning contract.

No current Runtime consumer imports MedCAT, DEEPMED Search, PubMed or a
provider HTTP SDK for Knowledge/Research. The inventory therefore does not
authorize an adapter migration yet.

## New application-owned boundaries

The stable application ports are defined in
`apps/runtime/src/ports/outbound/knowledge.py`:

```text
Clinical Runtime
      ├── KnowledgePort
      │      └── KnowledgeLookupQuery → KnowledgeResult
      └── ResearchPort
             └── ClinicalQuestion → ResearchResult
```

Future adapters may include:

```text
KnowledgePort
    ├── TerminologyAdapter
    └── MedCATAdapter              (future)

ResearchPort
    ├── LocalResearchAdapter       (possible)
    ├── PubMedAdapter              (possible)
    └── DeepMedSearchAdapter       (future)
```

The current reasoning implementation is not silently reclassified as one of
these adapters. Its migration requires a separate compatibility decision.

## Terminology and clinical context split

Terminology is a separate boundary from Knowledge enrichment:

```text
Canonical Evidence
      ↓
Clinical Normalization
      ↓
TerminologyPort
      ↓
TerminologyResult
      ↓
Canonical Clinical Concepts
```

The existing immutable `packages.terminology_sdk.TerminologyResult` is reused
by the application-owned `TerminologyPort`; no second result model was
created. The current deterministic normalization vocabulary remains the
behavior-preserving baseline and is not replaced by a provider in this
milestone.

Clinical context is a different boundary:

```text
Canonical Mention
      ↓
ClinicalContextPort
      ↓
ClinicalContextResult
```

The versioned state projection has a separate `ClinicalContextBuilderPort`:

```text
Clinical Facts
      ↓
ClinicalContextBuilderPort
      ↓
ClinicalContext
```

The Runtime context module and orchestration boundary use
`ClinicalContextBuilderPort`. medspaCy and NIEDE PT-BR rules are candidates for
the assertion-context port, not current dependencies.

## Immutability rule

The following are inputs or canonical evidence and must not be overwritten by
Knowledge, Research, Correlation or Representation:

```text
Raw Evidence       immutable
Canonical Evidence immutable
Transcript*        immutable contract values

KnowledgeResult    derived
ResearchResult     derived
Correlation        derived
Clinical State     derived projection/evolution
```

Enrichment may reference evidence IDs and provenance, but it cannot replace
the original text, payload, timestamps, identity, revision or provenance of
the source evidence.

## Next migration sequence

1. Keep the current Runtime behavior and internal reasoning path unchanged.
2. Add explicit compatibility tests around the new ports and immutable result
   contracts.
3. Define a separate use-case cutover for terminology enrichment.
4. Define a separate use-case cutover for external research retrieval.
5. Only then add concrete adapters and vendor integrations.
