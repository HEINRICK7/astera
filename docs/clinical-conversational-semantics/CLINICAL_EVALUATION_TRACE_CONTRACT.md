# Clinical Semantics Evaluation Trace Contract

Status: **Infrastructure only — no V7 rerun, no resolver repair**

This contract defines the minimum evidence required for a future clinical
semantics evaluation. It is a benchmark/observability boundary, not a domain
model and not a runtime resolver API.

## Scope and non-goals

The contract is intended to make a future one-shot diagnostic evaluation
explainable without rerunning the resolver. It does not modify the consumed V7
corpus, its gold, the frozen policy, or the resolver. The current V7 blind run
remains historical and consumed; it is not retrofitted with invented traces.

The implementation is in
`labs/terminology_benchmark/evaluation_trace.py`, and the machine-readable
schema is `labs/terminology_benchmark/data/EVALUATION_TRACE_SCHEMA.json`.

## Required identity

Every case trace records:

- `evaluation_id`
- `case_id`
- `corpus_version` and `corpus_checksum`
- `resolver_version` and `resolver_checksum`
- `policy_version`

These values are part of the saved evidence and are never inferred later.

## Ordered immutable stages

The append-only stage order is:

```text
input_segments
  → local_mentions
  → semantic_candidates
  → reference_resolution
  → ownership_resolution
  → cross_segment_state
  → resolved_semantics
  → generated_relations
  → final_projection
  → prediction
  → gold
  → comparison
```

Each `ClinicalStageSnapshot` stores an immutable payload, `input_hash`,
`output_hash`, a hash-chain link, decisions, preserved/changed/dropped fields,
and provenance. A stage cannot be appended twice, reordered, or silently
replaced. The API returns a new trace on append; it does not mutate an existing
trace.

`prediction` and `gold` are mandatory before a trace can be saved. Gold is a
snapshot of reference evidence, never a value reconstructed from predictions.

## Explicit trace types

- `ClinicalEvaluationTrace`: case identity and ordered snapshots.
- `ClinicalStageSnapshot`: immutable stage payload and transformation audit.
- `ClinicalDecisionTrace`: rule/policy decision, hashes, and provenance.
- `ClinicalMismatchTrace`: saved expected/actual mismatch for offline analysis.

The first-divergence analyzer consumes a saved `ClinicalEvaluationTrace` and an
optional gold payload. It does not import or execute the resolver and does not
assign G1–G4 classes. If a trace contains no explicit mismatch, a prediction vs
gold comparison is marked as inferred with confidence `0.5`; it is not claimed
to identify the causal stage.

## Invariants

`ClinicalEvaluationTrace.validate()` enforces:

- `trace_case_id_stable`
- `trace_stage_order_stable`
- `trace_no_prediction_loss`
- `trace_no_gold_mutation`
- `trace_provenance_complete`
- `trace_hash_chain_valid`

Serialization is deterministic JSON (`sort_keys=true`, UTF-8, stable SHA-256
payload hashes). Loading a modified payload, output hash, or chain hash fails
closed with `TraceContractError`.

## Offline first-divergence output

`FirstDivergenceAnalyzer` returns:

- `first_divergence_stage`
- `semantic_dimension`
- `expected` and `actual`
- `upstream_state` (saved stage/output hashes)
- `downstream_effects` (saved changed/dropped fields)
- `confidence`
- all saved mismatches

Example CLI:

```bash
.venv/bin/python -m labs.terminology_benchmark.analyze_evaluation_trace \
  path/to/trace.json
```

## Test boundary

Synthetic fixtures cover mention loss, antecedent error, ownership error,
temporality error, missing relation, and a preserved projection. They are
in `tests/benchmark/test_evaluation_trace.py` and contain no V7 data.

## Current gate

```text
V7                  CONSUMED / FAIL
V7 rerun            FORBIDDEN
resolver repair     NOT_AUTHORIZED
Shadow              BLOCKED
Production          BLOCKED
```

This milestone stops at the observability HUMAN GATE. A future Diagnostic Set
D1 requires a separate explicit authorization and must use this contract from
the start.
