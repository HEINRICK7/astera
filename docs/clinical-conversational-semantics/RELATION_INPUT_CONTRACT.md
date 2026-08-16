# Relation Input Contract

Status: proposed from the frozen D3 audit; not yet implemented.

The `ClinicalRelationCompiler` may compile only after `ResolvedClinicalSemantics` supplies the semantic truth required by the relation type. The compiler is not responsible for recovering omitted ownership, state or transition information.

## Required common contract

Every resolved relation input must provide:

- one resolved owner identity and a typed owner (`medication`, `treatment`, `symptom`, `condition`, or `anatomical` as applicable);
- the resolved current attribute value, if the relation is derived from an attribute;
- ownership for that attribute, including owner identity and source segment IDs;
- current-versus-historical state when both historical and current evidence exist;
- provenance that supports the value and relation;
- an explicit endpoint signal for relations not derived from an attribute.

Missing data must remain missing or unresolved. The compiler must not infer an owner from proximity or invent a transition.

## Relation-specific contract

| Relation | Required input | Forbidden shortcut |
| --- | --- | --- |
| `HAS_DOSE` | current `dose`, compatible medication/treatment owner, dose ownership and provenance | using a previous dose as current |
| `HAS_FREQUENCY` | current `frequency`, compatible medication/treatment owner, frequency ownership and provenance | copying frequency from an adjacent medication |
| `HAS_LATERALITY` | resolved `laterality`, symptom/condition/anatomical owner, laterality ownership and provenance | using a laterality cue without an owner |
| `CHANGED_FROM` | explicit transition evidence with target, previous value, owner and source provenance | treating the first observed value as both previous and current |
| `CHANGED_TO` | explicit transition evidence with target, current value, owner and source provenance | deriving a transition from an untyped pair of values |
| `DISCONTINUED_AT` | `status=discontinued`, medication/treatment owner, discontinuation evidence and provenance | emitting lifecycle relation for a symptom/event or from temporality alone |
| other explicit relations | typed source/target endpoint signal and relation provenance | silently defaulting endpoints |

## Authority boundary

```text
Local semantics / continuity
        ↓
ResolvedClinicalSemantics  -- must satisfy this contract
        ↓
ClinicalRelationCompiler
        ↓
Immutable Relation Set
```

The D3 audit found that `owner_type=null`, unresolved current state and malformed/missing transition evidence are upstream contract failures. This document is a diagnostic proposal only; policy, gold, resolver and compiler remain unchanged.
