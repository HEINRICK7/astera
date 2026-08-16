# V6 Repair V4 — Policy v1.1 Type-A Gate

Date: 2026-08-15  
Status: **FAIL — HUMAN GATE**  
Policy: `CLINICAL_SEMANTIC_POLICY` v1.1  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

Repair V4 was executed after the residual policy adjudication. It used the official frozen V6 corpus and was restricted to `TYPE_A_RESOLVER_ERROR`. The 10 `TYPE_B_GOLD_ISSUE` items were excluded from repair scope and were not used as a repair target.

## Result

| Metric | Repair V4 policy v1.1 |
|---|---:|
| mention exact match | 0.781437 |
| relation exact match | 0.918605 |
| scope accuracy | 0.980240 |
| cross-mention isolation | 0.627737 |
| cross-segment resolution | 0.620968 |
| speaker attribution | 1.000000 |
| provenance | 1.000000 |
| hard gate | **FAIL** |

Authority instrumentation:

```text
resolver_decisions_total       4092
resolver_decisions_preserved   4002
resolver_decisions_overwritten 90
legacy_fallback_count          0
ambiguous_forced_resolution    0
```

The complete machine-readable result is [context-validation-v6-repair-v4-policy-1.1-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/context-validation-v6-repair-v4-policy-1.1-2026-08-15.json).

## Gate state

```text
TYPE_A_RESOLVER_ERROR = 124
TYPE_B_GOLD_ISSUE     = 10
TYPE_C_POLICY_UNDEFINED = 0
gold_changes          = 0
resolver_changes      = 0 during this run
V6 checksum           = preserved
holdouts              = NOT_EXECUTED
Shadow                = BLOCKED
Production            = BLOCKED
```

Because the V4 hard gate failed, execution stops at the HUMAN GATE. No further resolver repair, V5/V6 iteration, holdout execution, gold change, Shadow Integration, or production promotion is authorized by this result.
