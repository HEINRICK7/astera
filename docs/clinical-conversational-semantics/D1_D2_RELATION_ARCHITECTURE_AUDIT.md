# D1/D2 Relation Semantics Architecture Audit

Status: **HUMAN GATE — no repair implemented**

Scope: frozen D1/D2 traces only. D1 and D2 were not rerun; resolver, policy, corpus and gold were not modified by this audit.

## Generated-relation findings

- D1 relation-first cases/findings: `15` cases / `18` findings
- D2 relation-first cases/findings: `14` cases / `14` findings

| Category | D1 | D2 | Total |
|---|---:|---:|---:|
| ATTRIBUTE_TO_RELATION_COMPILATION | 0 | 3 | 3 |
| CURRENT_VS_HISTORICAL_STATE | 1 | 4 | 5 |
| RELATION_DUPLICATION | 1 | 2 | 3 |
| RELATION_NORMALIZATION | 1 | 0 | 1 |
| RELATION_OWNER_SELECTION | 7 | 0 | 7 |
| RELATION_SUPPRESSION | 2 | 1 | 3 |
| TRANSITION_COMPILATION | 6 | 4 | 10 |

## Pattern interpretation

- `ATTRIBUTE_TO_RELATION_COMPILATION`: resolved attributes exist but the derived HAS_* relation is absent or stale. This is the clearest compiler-boundary class.
- `TRANSITION_COMPILATION`: CHANGED_FROM is missing or emitted without a coherent current transition.
- `CURRENT_VS_HISTORICAL_STATE`: the resolved state already differs from gold, and relation output follows that wrong state. A compiler alone cannot repair this upstream semantic error.
- `RELATION_OWNER_SELECTION`: a relation is emitted for an incompatible owner or entity type.
- `RELATION_NORMALIZATION`: same relation family has a conflicting value/representation, including local and resolved values coexisting.
- `RELATION_DUPLICATION`: duplicate relation keys appear in the expected or produced set; several D1/D2 discontinued findings are expected-side explicit-plus-derived duplication.
- `RELATION_SUPPRESSION`: an expected relation is absent without sufficient resolved evidence to attribute the loss to a compiler-only omission.

## Writer topology

The writer inventory identifies six relation-writing sites across five competing components. Relation creation occurs both before and after context resolution, and transition code mutates an existing projection relation list. This is inconsistent with a single immutable relation authority.

## Recommendation

**R2 — consolidate writers in a single ClinicalRelationCompiler** is recommended for the relation subsystem, with an explicit limitation: it should be proposed and tested as a boundary consolidation, not assumed to solve the 14 D2 prediction/semantic indeterminate cases or upstream state errors.

R1 is insufficient because the same relation vocabulary is produced and mutated in multiple components. R3 is not yet justified because the traces do not prove that the relation representation itself cannot express the required semantics. R4 is unsupported: G4 remains zero and no external capability evidence exists.
