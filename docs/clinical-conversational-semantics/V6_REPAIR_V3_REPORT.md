# V6 Repair V3 Report — Candidate Quality & Ownership

Date: 2026-08-15  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`  
Status: **FAIL — HUMAN GATE**

The internal candidate-quality fixture gate passed. Repair V3 was then executed once against the frozen official V6 corpus. The final V6 gate did not pass.

| Run | Mention exact | Relation exact | Cross mention isolation | Cross-segment | Provenance |
|---|---:|---:|---:|---:|---:|
| Blind | 0.7216 | 0.7442 | 0.5766 | 0.4597 | 1.0000 |
| Repair V1 | 0.7695 | 0.7442 | 0.6204 | 0.5887 | 1.0000 |
| Repair V2 | 0.7754 | 0.8140 | 0.6204 | 0.6048 | 1.0000 |
| Authoritative Cutover | 0.7754 | 0.8140 | 0.6204 | 0.6048 | 1.0000 |
| Repair V3 | 0.7485 | 0.8140 | 0.5766 | 0.5323 | 1.0000 |

V3 therefore preserved relation quality and provenance but regressed mention composition and cross-segment resolution. Authority instrumentation reported:

```text
resolver_decisions_total       4092
resolver_decisions_preserved   3930
resolver_decisions_overwritten  162
legacy_fallback_count          0
ambiguous_forced_resolution    0
```

The machine-readable result is [context-validation-v6-repair-v3-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/context-validation-v6-repair-v3-2026-08-15.json).

No holdout was evaluated. V7, shadow integration, and production promotion remain blocked.

After the projection integrity gate passed, the V6 run was repeated once with the same frozen checksum; the metrics remained identical. See [V6_RESOLVED_VS_GOLD_FAILURE_ANALYSIS.md](/home/carlos-henrique/Documentos/workspace/astera/docs/clinical-conversational-semantics/V6_RESOLVED_VS_GOLD_FAILURE_ANALYSIS.md).
