# Resolved Semantics vs Gold Alignment Audit — V6

Date: 2026-08-15  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`  
Corpus and resolver modified for this audit: **no**

This document is the frozen pre-repair baseline. The formal gate, with the required labels and dimensional counts, is [V6_SEMANTIC_ALIGNMENT_HUMAN_GATE.md](V6_SEMANTIC_ALIGNMENT_HUMAN_GATE.md).

The audit compares the resolved stage captured by the end-to-end trace against the frozen gold. It does not infer that every mismatch is a resolver bug.

| Finding | Count |
|---|---:|
| records with divergence | 89 |
| field/relation findings | 134 |
| `TYPE_A_RESOLVER_ERROR` | 68 |
| `TYPE_B_GOLD_ISSUE` | 0 |
| `TYPE_C_POLICY_UNDEFINED` | 66 |
| gold review queue | 47 |

| Category | Count |
|---|---:|
| WRONG_NEGATION | 25 |
| WRONG_TEMPORALITY | 24 |
| WRONG_STATUS | 48 |
| WRONG_LATERALITY | 8 |
| WRONG_DOSE | 2 |
| WRONG_FREQUENCY | 3 |
| WRONG_EXPERIENCER | 1 |
| MISSING_RELATION | 15 |
| WRONG_RELATION | 4 |
| EXTRA_RELATION | 4 |

The largest Type C clusters are `status=present` versus `status=null` and the gold relation vocabulary `DISCONTINUED_AT`. These require policy approval before code changes. Type A clusters include explicit negation scope, explicit laterality, family experiencer, historical-event cues, cross-segment medication-state leakage, and in-segment dose/frequency transitions.

Mention-level wrong/missing/extra detection is not asserted by this audit because the trace is query-per-gold and therefore does not independently enumerate mention candidates. Those categories remain unassessed rather than being reported as zero.

The findings decompose into 45 Type A cases / 52 mentions / 14 relations / 54 fields and 44 Type C cases / 63 mentions / 9 relations / 57 fields. These dimensions overlap and are not additive. Type B remains unestablished; the 47 review items are queue-only.

The complete case-level trace, with text/segments, expected, resolved, differing fields, reason, confidence, and type, is [v6-resolved-gold-alignment-audit-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/v6-resolved-gold-alignment-audit-2026-08-15.json).
