# Clinical Relation Compiler — Cutover Map

Status: R2 implementation complete; frozen-candidate gate pending final verification.

## Authoritative flow

```text
ResolvedClinicalSemantics
        ↓
ClinicalRelationCompiler
        ↓
ClinicalRelationSet (immutable)
        ↓
AuthoritativeProjectionWriter
        ↓
ClinicalContextResult.provenance["projection"]["relations"]
```

`ResolvedClinicalSemantics` is the semantic boundary. The compiler consumes
resolved values, ownership, transitions and provenance; it does not resolve
antecedents or infer clinical attributes.

## Writer migration

| Previous location | Cutover role | Final relation authority |
| --- | --- | --- |
| `context_safety.py` | Emits `relation_signals` from local evidence | No |
| `cross_segment_context.py` | Adds contextual transition signals and ownership evidence | No |
| `ClinicalRelationResolver` | Produces intermediate relation signals | No |
| `ClinicalRelationMaterializer` | Legacy compatibility API only | No |
| `ClinicalRelationCompiler` | Compiles the immutable final relation set | Yes |
| `AuthoritativeProjectionWriter` | Serializes the compiler output once | Serialization only |

The six audited relation sites now feed semantic signals or resolved evidence.
No local or contextual writer mutates the final projection relation list.

## Compiler responsibilities

The compiler owns materialization of derived relations such as `HAS_DOSE`,
`HAS_FREQUENCY`, `HAS_ROUTE`, `HAS_LATERALITY`, and medication lifecycle
relations such as `DISCONTINUED_AT`. It also normalizes transition signals such
as `CHANGED_FROM` to the resolved owner and removes duplicate final relations.

It does not decide:

- mention identity or antecedents;
- negation, certainty, temporality, experiencer or laterality values;
- dose, frequency or status values;
- clinical ownership or transition meaning.

Those decisions must already be represented in `ResolvedClinicalSemantics`.

## Scope and preserved evidence

This cutover changes only relation authority and materialization. Policy, gold,
V7, D1, D2 and their checksums are untouched. No historical benchmark is
rerun by this milestone.
