# V6 Repair V4 — Resolved Semantics Alignment

Date: 2026-08-15  
Scope: Type-A-only repairs  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`  
Status: **FAIL — HUMAN GATE**

| Run | Mention exact | Relation exact | Scope | Cross-segment | Provenance |
|---|---:|---:|---:|---:|---:|
| Repair V2 | 0.7754 | 0.8140 | 0.9671 | 0.6048 | 1.0000 |
| Repair V3 | 0.7485 | 0.8140 | 0.9653 | 0.5323 | 1.0000 |
| Repair V4 | 0.7814 | 0.9186 | 0.9802 | 0.6210 | 1.0000 |

V4 repaired only explicit Type-A defects: negation clause scope, laterality attachment distance, family cues, `virou` dose/frequency transitions, and short-answer owner isolation. Candidate generation, ownership policy, projection, and the frozen corpus were not changed.

Authority instrumentation for this run:

```text
resolver_decisions_total       4092
resolver_decisions_preserved   4002
resolver_decisions_overwritten  90
legacy_fallback_count          0
ambiguous_forced_resolution    0
```

The complete result is [context-validation-v6-repair-v4-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/context-validation-v6-repair-v4-2026-08-15.json).

V4 still fails the unchanged V6 thresholds. Holdouts, V7, Shadow Integration, and production promotion remain blocked.
