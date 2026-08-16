# SEM-STATUS-001 v1.2 — V6 Status Reclassification

Status: **HUMAN GATE — REPAIR V6 NOT AUTHORIZED**  
Policy: `SEM-STATUS-001`  
Version: `1.2`  
Decision: **APPROVED — documentation only**  
V6 checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

## Scope

The 90 status findings were reclassified against the approved v1.2 normative default. This does not alter resolver output, gold, corpus, or benchmark history.

## Result

- status findings: **90**
- status-only failures: **89**
- normative null: **90**
- explicit lifecycle: **0**
- medication lifecycle: **0**

| Classification | Count |
|---|---:|
| TYPE_A_RESOLVER_ERROR | 81 |
| TYPE_B_GOLD_ISSUE | 9 |
| TYPE_C_POLICY_UNDEFINED | 0 |
| ALIGNED | 0 |

## Status transitions

| Gold → resolved | Reclassified result | Count |
|---|---|---:|
| None → historical | TYPE_A_RESOLVER_ERROR | 18 |
| None → present | TYPE_A_RESOLVER_ERROR | 63 |
| present → None | TYPE_B_GOLD_ISSUE | 9 |

## Interpretation

- `None → present` and `None → historical` are resolver errors under v1.2 when no explicit lifecycle cue exists.
- `present → None` is a gold inconsistency under v1.2 for these nine assertion-only cases; gold remains untouched and review-only.
- `sim-v6-0040` remains a status Type B finding here, while its separate negation mismatch remains visible in the source audit.
- The full V6 status gate also audits gold values that matched v1.1 before the policy change. It exposes 30 additional `present`/`historical` values for gold review, bringing the complete v1.2 status review queue to 39 items.

## Invariants

- policy_changes: **documentation only**
- resolver_changes: **0**
- gold_changes: **0**
- corpus_changes: **0**
- checksum: **preserved**
- Repair V6: **NOT AUTHORIZED**
- holdouts: **NOT_EXECUTED**
- V7 / Shadow / Production: **BLOCKED**

The complete item-level queue is in `STATUS_V1_2_RECLASSIFICATION.json`.
