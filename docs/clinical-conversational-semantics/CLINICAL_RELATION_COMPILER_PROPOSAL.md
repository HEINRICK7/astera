# Clinical Relation Compiler Proposal

Status: **PROPOSAL ONLY — not implemented**

## Recommendation

R2 — consolidate relation writers in one deterministic compiler boundary.

The proposal is supported by the writer inventory and the repeated D1/D2 relation-first findings. It is not authorization for a repair or a resolver redesign.

## Proposed contract

```text
ResolvedClinicalSemantics
  ├── resolved_mentions
  ├── resolved_attributes
  ├── ownership
  ├── current/historical state
  ├── transitions
  └── provenance
          ↓
ClinicalRelationCompiler.compile()
          ↓
immutable ClinicalRelationSet
          ↓
ClinicalProjection
```

The compiler must be the only component allowed to create the final relation set. Local semantics may create candidates, but not final relations. Transition detection may produce transition evidence, but not append directly to projection. Projection may serialize the immutable set, but not infer or mutate relations.

## Inputs

- resolved mentions and stable mention IDs
- resolved attributes with exactly one owner
- owner/entity type
- current versus historical state
- transition evidence, including previous values
- field and event provenance

## Output rules

- emit current `HAS_DOSE`, `HAS_FREQUENCY`, `HAS_ROUTE`, `HAS_LATERALITY` only when owner/type and current value are valid;
- emit `CHANGED_FROM` only from explicit transition evidence;
- emit `DISCONTINUED_AT` only from current medication lifecycle state plus event provenance;
- deduplicate by semantic relation key;
- reject incompatible owner/type relations;
- bind provenance during compilation and make the output immutable;
- never fall back to local relation output after compilation.

## What this would and would not eliminate

The audit found `3` attribute-to-relation findings, `10` transition findings, `7` owner-selection findings, `1` normalization findings and `3` duplication findings across D1/D2 relation-first traces.

A single compiler should structurally eliminate competing-writer behavior, stale local relation survival, post-resolution append races and compiler-side provenance drift. It will not by itself correct a wrong resolved dose/status/temporality or a missing antecedent; those remain upstream semantic evidence and must be tested separately.

## Required future validation

1. Freeze a new diagnostic set; do not rerun D1/D2.
2. Compare compiler input truth with gold before judging compiler output.
3. Require immutable relation-set hash, one owner per attribute, unique endpoints and provenance completeness.
4. Report compiler-boundary failures separately from upstream resolved-semantics failures.
5. Keep the 14 D1/D2 prediction indeterminates outside repair authorization until Trace v2 or a new diagnostic set identifies their first divergence.

Next gate: human authorization is required before implementing the compiler.
