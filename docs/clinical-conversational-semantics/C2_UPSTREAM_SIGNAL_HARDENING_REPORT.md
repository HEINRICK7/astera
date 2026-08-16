# C2 Upstream Signal Hardening Report

Status: **HUMAN GATE**

## Scope

This milestone hardened the boundary immediately before
`ClinicalRelationCompiler`. It did not change the compiler, policy, gold,
corpora or consumed benchmarks. D1, D2 and D3 were not rerun.

## Implementation

- Added typed `ResolvedAttributeSignal`.
- Added typed `ResolvedTransitionSignal`.
- Added `RelationInputContractReport` with four structural gate metrics.
- Added explicit `RESOLVED`, `UNRESOLVED_OWNER`, `UNRESOLVED_STATE` and
  `AMBIGUOUS` statuses.
- Integrated signals into `ResolvedClinicalSemantics` and the cross-segment
  upstream materialization boundary.
- Blocking signals now produce `UNRESOLVED` resolution and do not reach the
  final relation compiler path as silently usable inputs.
- Kept the compiler implementation unchanged.

## Gates

```text
dedicated C2 signal tests       PASS
relation/compiler regressions   PASS
compileall                      PASS
```

Test result: **51 passed**.

The structural contract yields 1.00 for every relation-ready synthetic signal.
Invalid signals are represented explicitly and blocked rather than promoted
to fabricated certainty.

## Decision

```text
ClinicalRelationCompiler   FROZEN
C2 upstream hardening       IMPLEMENTED / HUMAN GATE
D4                         BLOCKED until explicit authorization
D1/D2/D3/V7                CONSUMED / IMMUTABLE
Compiler repair             BLOCKED
LLM/provider                NOT JUSTIFIED
Shadow                      BLOCKED
Production                  BLOCKED
```

This report proves contract hardening and regression safety only. It is not an
unseen generalization result; D4 remains a separate future benchmark and must
not be created or executed by this milestone.
