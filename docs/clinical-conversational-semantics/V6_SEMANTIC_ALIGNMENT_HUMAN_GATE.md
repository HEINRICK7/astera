# V6 Resolved Semantics vs Gold — Pre-Repair HUMAN GATE

Date: 2026-08-15  
Status: **REPAIR V4 FAIL — HUMAN GATE**  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

This is the pre-repair alignment gate. It consolidates the frozen V6 audit into explicit resolver, gold, and policy categories. It does not alter resolver code, gold annotations, or the V6 corpus.

## Required order and current state

| Stage | Status |
|---|---|
| Resolved vs Gold Audit | complete |
| Error classification A/B/C | complete |
| Clinical Semantic Policy | v1.0 approved for the three adjudicated clusters |
| Gold Review Queue | 47 items adjudicated; no gold changes |
| HUMAN GATE | **reopened after V4 hard-gate failure** |
| Resolver Repair V4 | **executed Type-A-only; FAIL** |

## Classification summary

The denominator for percentages is the 134 field/relation findings. Case, mention, relation, and field counts are dimensions of the findings and are not intended to sum to 134.

| Type | Cases | Mentions | Relations | Fields | Findings | % of total errors |
|---|---:|---:|---:|---:|---:|---:|
| `TYPE_A_RESOLVER_ERROR` | 45 | 52 | 14 | 54 | 68 | 50.746% |
| `TYPE_B_GOLD_ISSUE` | 0 | 0 | 0 | 0 | 0 | 0.000% |
| `TYPE_C_POLICY_UNDEFINED` | 44 | 63 | 9 | 57 | 66 | 49.254% |
| **Total findings** | — | — | — | — | **134** | **100.000%** |

The audit established no Type B gold issue automatically. The 47 `GOLD_REVIEW_REQUIRED` items remain a human-review queue; they are not approved gold changes.

## Aggregate divergence by field/category

| Field/category | Findings | Interpretation |
|---|---:|---|
| mention | unassessed | The query-per-gold trace does not independently enumerate wrong, missing, or extra mentions; this is not zero. |
| negation | 25 | `WRONG_NEGATION` |
| certainty | 0 | No certainty divergence was recorded. |
| temporality | 24 | `WRONG_TEMPORALITY` |
| experiencer | 1 | `WRONG_EXPERIENCER` |
| laterality | 8 | `WRONG_LATERALITY` |
| status | 48 | `WRONG_STATUS`; primarily `present` versus `null` policy vocabulary. |
| dose | 2 | `WRONG_DOSE` / dose-value representation. |
| frequency | 3 | `WRONG_FREQUENCY` / transition ownership. |
| relation | 23 | 15 missing, 4 wrong, 4 extra relations. |
| cross_segment | 108 | Overlapping dimension: records with cross-segment context; not additive with field rows. |

## Interpretation boundary

Type A findings are explicit, policy-independent resolver defects identified by the audit, such as target-scoped negation, unambiguous laterality, family experiencer, historical-event cues, and clear transition ownership.

Type C findings are not eligible for repair until policy is approved. The main clusters are current-state `status` vocabulary and the `DISCONTINUED_AT` relation contract. A clinically plausible interpretation is not enough to silently change either code or gold.

The normative rules are in [CLINICAL_SEMANTIC_POLICY.md](CLINICAL_SEMANTIC_POLICY.md), with stable IDs `SEM-STATUS-001`, `SEM-TEMP-001`, `SEM-NEG-001`, `SEM-EXP-001`, `SEM-DOSE-001`, `SEM-XSEG-001`, and `SEM-REL-001`.

## Required gate outputs

| Gate output | Value |
|---|---|
| `TYPE_A count` | 68 findings / 45 cases |
| `TYPE_B count` | 0 findings / 0 cases |
| `TYPE_C count` | 66 findings / 44 cases |
| `gold_review_required` | 47 |
| `semantic_policy_rules_created` | 7 (6 required semantic IDs + relation vocabulary rule) |
| `resolver_changes` | 0 in this pre-repair gate |
| `gold_changes` | 0 |
| `corpus_changes` | 0 |
| `V6 checksum` | preserved: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10` |
| `holdouts` | `NOT_EXECUTED` |

## HUMAN GATE decision

**Repair V4 remains blocked.** Human approval is required for the policy rules and the 47-item gold review queue before any resolver repair is authorized. No automatic gold update is permitted.

The next milestone is [Semantic Policy Adjudication — V6](V6_SEMANTIC_POLICY_ADJUDICATION.md). It must resolve the 47 queue items and freeze the policy version before any Type A repair proposal is considered.

The earlier V4 execution is retained only as historical diagnostic evidence in [V6_RESOLVED_VS_GOLD_FAILURE_ANALYSIS.md](V6_RESOLVED_VS_GOLD_FAILURE_ANALYSIS.md); it is not an authorization to continue repair in this gate. No new repair or V6 rerun was performed while preparing this report.

The final post-adjudication result is [v6-residual-type-c-adjudication-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/v6-residual-type-c-adjudication-2026-08-15.json). It records global `TYPE_A=124`, `TYPE_B=10`, `TYPE_C=0`. The Type-A-only V4 result is recorded in [V6_REPAIR_V4_POLICY_1_1_REPORT.md](V6_REPAIR_V4_POLICY_1_1_REPORT.md) and failed the hard gate; the workflow is stopped at HUMAN GATE.

Sources: [resolved/gold audit](V6_RESOLVED_GOLD_ALIGNMENT_AUDIT.md), [gold review queue](V6_GOLD_REVIEW_QUEUE.md), and the machine-readable [frozen audit result](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/v6-resolved-gold-alignment-audit-2026-08-15.json).
