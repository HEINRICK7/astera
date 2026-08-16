# Repair V5 Plan — V6 Type A Only

Status: **PLAN ONLY — HUMAN GATE**

No implementation is authorized by this document. The plan orders future work by causal dependency, not by raw error count.

## Proposed order

1. `ROOT-ATTRIBUTE-OWNERSHIP` and `ROOT-TRANSITION-OWNERSHIP` — validate owner invariants and current-versus-historical transitions.
2. `ROOT-NEGATION-SCOPE` — validate target-scoped negation and its interaction with mention scope.
3. `ROOT-STATUS` — materialize policy v1.1 status without allowing negation or ownership leakage.
4. `ROOT-TEMPORAL-OWNERSHIP` — resolve event/state temporality without assigning it to experiencer references.
5. `ROOT-RELATION-RESOLUTION` — repair only after upstream ownership/status/transition gates pass.
6. `ROOT-CROSS-SEGMENT-OWNERSHIP` — validate context inheritance after local semantics are stable.

## Required per-phase gates

- synthetic and invariant tests;
- candidate and projection integrity gates;
- RAW V6 score retained for historical comparison;
- POLICY-ALIGNED V6 score as the quality gate;
- Type B items excluded from repair targets and kept in the review queue;
- no holdouts until the staged Type-A sequence passes HUMAN GATE.

## Current authorization

```text
Repair V5 = NOT AUTHORIZED
V6 = FROZEN
Policy = v1.1 FROZEN
Type B = UNTOUCHED
Holdouts = NOT_EXECUTED
V7 = BLOCKED
Shadow = BLOCKED
Production = BLOCKED
```
