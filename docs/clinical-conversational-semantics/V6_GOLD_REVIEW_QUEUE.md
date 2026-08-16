# V6 Gold Review Queue

Status: **ADJUDICATED — POLICY v1.0**

This queue contains 47 suspected policy/contract mismatches across 34 cases. It is review-only: no gold annotation was modified and no resolver behavior was changed from this queue.

Main clusters:

- 37 cases where gold uses `status=present` while the resolver contract emits `null` for a current assertion;
- 5 cases requiring a decision about `DISCONTINUED_AT` relation vocabulary;
- 5 additional status vocabulary/ownership cases.

The item-level queue, including expected value, resolved value, confidence, and review reason, is in the `gold_review_queue` field of [v6-resolved-gold-alignment-audit-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/v6-resolved-gold-alignment-audit-2026-08-15.json).

No `TYPE_B_GOLD_ISSUE` was established. Carlos Henrique adjudicated all 47 items under policy v1.0. The queue is not evidence that the gold is wrong; no gold annotation was changed and V6 remains frozen.

This queue is part of the adjudication record in [V6_SEMANTIC_POLICY_ADJUDICATION.md](V6_SEMANTIC_POLICY_ADJUDICATION.md). The residual adjudication reclassified 10 items as `TYPE_B_GOLD_ISSUE`; they remain review-only and must not be used to drive Repair V4. See [V6_RESIDUAL_GOLD_REVIEW_QUEUE.md](V6_RESIDUAL_GOLD_REVIEW_QUEUE.md).
