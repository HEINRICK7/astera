# Trace Granularity v2 Contract

Status: **Authorized infrastructure; no D1 rerun**

Trace v2 extends `ClinicalEvaluationTrace` without changing the clinical
resolver or semantic policy. Existing `clinical-evaluation-trace/v1` files
remain readable and retain their original hash-chain semantics.

## Additional per-stage evidence

For the `semantic_candidates`, `reference_resolution`,
`ownership_resolution`, `generated_relations`, and `final_projection` stages,
v2 requires these immutable maps:

- `per_mention_attributes`
- `per_mention_relations`
- `candidate_to_resolved_field_map`
- `ownership_decisions`
- `relation_generation_inputs`
- `relation_generation_outputs`
- `projection_field_map`
- `dropped_fields_by_stage`
- `transformed_fields_by_stage`

Empty maps are valid when a stage has no value for a field; absence is not.
The maps are included in the stage hash chain, so editing granularity evidence
invalidates the trace.

## Boundary questions answered

With v2, an evaluator can distinguish:

```text
candidate field
  → resolved field
  → owned field
  → relation input
  → generated relation
  → projected field/relation
  → prediction
```

Each map is per mention and preserves dropped and transformed fields rather
than overwriting them. This is specifically intended to resolve the 16 D1
cases that were previously only observable as
`final_projection == prediction != gold`.

## Compatibility and safety

- v1 traces load unchanged.
- v2 traces use `clinical-evaluation-trace/v2`.
- No D1 or V7 trace is rewritten or used as a fixture.
- No live resolver is required by the offline analyzer.
- Relation repair and trace granularity are independent concerns.

The machine-readable schema is
`labs/terminology_benchmark/data/TRACE_GRANULARITY_V2_SCHEMA.json`.

