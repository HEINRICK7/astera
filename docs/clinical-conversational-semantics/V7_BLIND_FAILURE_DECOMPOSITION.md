# V7 Blind Failure Decomposition

Status: **HUMAN GATE — DIAGNOSTIC LIMITATION**

The single V7 Blind Run was not rerun. The preserved artifact contains aggregate metrics, family/entity/scope groups, and field mismatch counts, but no per-case predictions or traces.
Therefore `case_id`, `expected → predicted`, `first_divergence_stage`, and causal G1–G4 classification cannot be asserted without inventing evidence.

## Observed aggregate evidence

- `negated`: `0.452012`
- `certainty`: `1.000000`
- `temporality`: `0.851393`
- `experiencer`: `0.913313`
- `laterality`: `0.140496`
- `dose`: `0.571429`
- `dose_value`: `0.571429`
- `dose_unit`: `0.842857`
- `frequency`: `0.614035`
- `route`: `1.000000`
- `status`: `0.250000`
- `mention_exact_match`: `0.089783`
- `relation_exact_match`: `0.541436`
- `cross_mention_isolation`: `0.000000`
- `cross_segment_resolution`: `0.113537`
- `provenance`: `1.000000`

## Observed mismatch dimensions (not causal root causes)

- `mention:status`: `180`
- `mention:negated`: `177`
- `mention:laterality`: `104`
- `relation_mismatch`: `83`
- `mention:dose`: `60`
- `mention:dose_value`: `60`
- `mention:temporality`: `48`
- `mention:frequency`: `44`
- `mention:experiencer`: `28`
- `mention:dose_unit`: `22`

## Causal classification status

- Confirmed G1: `0`
- Confirmed G2: `0`
- Confirmed G3: `0`
- Confirmed G4: `0`
- All per-case G1–G4 assignments: `NOT_DETERMINABLE`
- G4/LLM evidence: `NOT PROVEN`

## Top failing scenario families (observed mention exact)

- `ANAPHORA_SPEAKER_TRANSITION`: `0.000000`
- `DISTRIBUTED_TEMPORALITY`: `0.000000`
- `DOSE_TRANSITION`: `0.000000`
- `FAMILY_PATIENT_EXPERIENCER`: `0.000000`
- `MEDICATION_RECONCILIATION`: `0.000000`

## First divergence

Not observable in the preserved Blind Run artifact. The aggregate pattern supports an architectural hypothesis around cross-turn reference/state/ownership, but does not prove whether the first divergence is mention detection, antecedent resolution, ownership, or relation generation.

## Required next milestone

Add an immutable per-case prediction and semantic trace contract to a future authorized evaluation path. The trace must preserve candidate, resolved, projected, evaluated, expected, first divergence stage, and downstream effects. This is an observability/causal-attribution milestone, not Repair V8.

Hard stops: no repair, no V7 rerun, no gold/corpus change, Shadow blocked, Production blocked.
