# D1 Relation Repair Report

Status: **HUMAN GATE — repair implemented, frozen benchmark not rerun**

## Scope

This change addresses only the deterministic relation boundary identified by
the D1 audit. It does not change reference resolution, attribute ownership,
temporality, negation, semantic policy, V7, D1 gold, or frozen D1 traces.

The 15 D1 relation-first-divergence cases remain consumed evidence. They were
not used as approval fixtures and D1 was not rerun.

## Implemented mechanisms

`ClinicalRelationMaterializer` now:

- materializes `HAS_DOSE`, `HAS_FREQUENCY`, `HAS_ROUTE`, and
  `HAS_LATERALITY` only for permitted owner types;
- materializes `DISCONTINUED_AT` only for medication/treatment lifecycle;
- removes stale derived relations whose value is not the resolved current
  attribute;
- preserves valid `CHANGED_FROM` relations;
- deduplicates semantic relation keys;
- preserves field-level source segment provenance;
- rewrites an otherwise-valid derived relation with the authoritative
  resolved-field provenance, so a local relation cannot mask the segment that
  supplied the resolved attribute;
- avoids attaching medication frequency/dose relations to symptom or family
  mentions when ownership is unavailable.

Transition relation generation now handles frequency transitions independently
of dose transitions and does not fabricate a dose transition when no dose
transition evidence exists.

## Synthetic engineering gate

The new tests are independent of D1, V7, and the trace fixtures:

- current dose replaces stale `HAS_DOSE` while `CHANGED_FROM` survives;
- symptom ownership rejects medication frequency materialization;
- duplicate `DISCONTINUED_AT` is collapsed;
- unknown owner rejects derived relation creation;
- authoritative field provenance replaces stale local relation provenance;
- Trace v2 serialization, required granularity, and schema validation pass.

Results:

```text
focused relation/trace/legacy gate PASS (48)
trace v2 tests               PASS
legacy v1 trace load         PASS (36/36 D1 traces)
trace v2 JSON schema         PASS
```

## Architecture fitness

```text
reference resolution touched     FALSE
attribute ownership touched      FALSE
temporality/negation touched     FALSE
policy changed                   FALSE
case_id-specific rule added      FALSE
D1/V7 rerun                     FALSE
```

The repair is contained at relation normalization/materialization and the
existing transition-relation seam. It is not a new conversational inference
architecture.

## Regression status

No frozen benchmark was rerun. The relation repair remains subject to a future
new diagnostic evaluation with Trace Granularity v2. D1's 16 indeterminate
cases remain indeterminate and were not repaired.

```text
D1                  CONSUMED
D1 rerun            FORBIDDEN
Relation repair     IMPLEMENTED / HUMAN GATE
Indeterminate fix   NOT AUTHORIZED
V7                  CONSUMED / FAIL
Shadow              BLOCKED
Production          BLOCKED
```
