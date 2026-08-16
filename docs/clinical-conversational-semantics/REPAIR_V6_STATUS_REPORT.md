# Repair V6 — Status-Only Report

Status: **POLICY-ALIGNED V6 PASS — HOLDOUTS NOT YET AUTHORIZED**  
Scope: `STATUS ONLY`  
Policy: `SEM-STATUS-001 v1.2`  
V6 checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

## Policy-aligned score

The quality gate excludes 39 status gold-review items exposed by v1.2 and 10 pre-existing Type B fields. Gold and corpus remain untouched.

| Metric | Score | Gate |
|---|---:|---|
| mention_exact_match | 0.9940 | PASS |
| relation_exact_match | 1.0000 | PASS |
| cross_mention_isolation | 0.9854 | PASS |
| cross_segment_resolution | 0.9839 | PASS |
| speaker_attribution | 1.0000 | PASS |
| provenance | 1.0000 | PASS |
| status | 1.0000 | PASS |

Overall policy-aligned gate: **PASS**.

## Raw V6 score

| Metric | Score |
|---|---:|
| mention_exact_match | 0.8593 |
| relation_exact_match | 1.0000 |
| cross_mention_isolation | 0.7664 |
| cross_segment_resolution | 0.6532 |
| provenance | 1.0000 |

The raw score remains the historical benchmark view and is not rewritten.

## Gold review expansion

- status findings from the prior v1.1 queue: **9**;
- additional status gold values exposed by v1.2: **30**;
- complete status gold-review queue: **39**;
- pre-existing non-status Type B fields: **10**;
- total excluded fields in the policy gate: **49**.

No Type B item was imitated by the resolver and no gold item was modified.

## Safety state

- resolver scope: status policy only;
- resolver changes: 1 policy-scoped behavior change;
- gold changes: 0;
- corpus changes: 0;
- holdouts `sim-v6-0056`–`sim-v6-0058`: **NOT_EXECUTED**;
- V7, Shadow Integration, and Production: **BLOCKED**.

The resolver may now be frozen for human confirmation. Holdout execution is a separate gate and has not been run by this report.

Complete machine-readable result: `context-validation-v6-repair-v6-status-final-2026-08-15.json`.
