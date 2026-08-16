# V7 Unseen Generalization Foundation

Status: **DRAFT ONLY — HUMAN REVIEW REQUIRED**

The V7 foundation contains 240 new PT-BR multi-turn conversation candidates.
The draft is disjoint by exact text from the checked V3–V6 sources and
consumed holdout sources. It is not an official evaluation corpus.

## Scenario distribution

Each family contains 20 cases:

- medication reconciliation
- dose transition
- frequency/status transition
- multiple symptoms
- family vs patient experiencer
- negation reversal
- distributed temporality
- topic switching
- elliptical answers
- clinician correction
- patient self-correction
- anaphora and speaker transition

All cases contain 5–6 dialogue turns. The draft contains no `GoldMention`, no
approved decision, and no automatically generated semantic gold.

## Required gates

V7 official evaluation remains blocked until all three conditions are true:

1. human review complete;
2. gold validation complete;
3. corpus freeze complete.

The guarded harness refuses execution while any condition is false. Resolver
and Semantic Policy v1.2 remain frozen. Old holdouts and the post-repair v2
holdout are not reused.

Artifacts:

- draft corpus: `labs/terminology_benchmark/data/v7_unseen_generalization_draft.jsonl`
- human queue: `labs/terminology_benchmark/results/v7-human-review-queue-2026-08-15.json`
- manifest: `labs/terminology_benchmark/results/v7-corpus-manifest-2026-08-15.json`
- disjointness: `labs/terminology_benchmark/results/v7-disjointness-report-2026-08-15.json`
- guarded harness: `labs/terminology_benchmark/run_v7_unseen_generalization.py`

Current state: `V7 BLOCKED`, `Shadow BLOCKED`, `Production BLOCKED`.
