# MILESTONE 1 — Residual Error Analysis V1

Status: **DONE**. Corpus: V6 oficial congelado; checksum `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`.

The machine-readable source is `labs/terminology_benchmark/results/context-cross-segment-residual-analysis-v6-2026-08-15.json`. It compares Blind Baseline with Repair V1 and excludes reserved cases.

## Metrics

| Metric | Blind | Repair V1 |
|---|---:|---:|
| mention exact | 0.7216 | 0.7695 |
| relation exact | 0.7442 | 0.7442 |
| scope accuracy | 0.9635 | 0.9743 |
| cross-mention isolation | 0.5766 | 0.6204 |
| cross-segment resolution | 0.4597 | 0.5887 |
| speaker attribution | 0.9677 | 0.9919 |
| provenance | 1.0000 | 1.0000 |

## Required taxonomy

Counts below are residual occurrences after Repair V1. A zero is an observed zero in the report, not an assumed pass.

| Layer | Category | Count | Affected cases | Affected mentions | Likely layer |
|---|---|---:|---:|---:|---|
| CONTEXT_STATE | STALE_CONTEXT | 0 | 0 | 0 | lifetime policy |
| CONTEXT_STATE | CONTEXT_OVERWRITE | 0 | 0 | 0 | state transitions |
| REFERENCE_RESOLUTION | WRONG_ANTECEDENT | 0 | 0 | 0 | antecedent scoring |
| REFERENCE_RESOLUTION | AMBIGUOUS_ANTECEDENT | 0 | 0 | 0 | ambiguity policy |
| REFERENCE_RESOLUTION | UNRESOLVED_REFERENCE | 0 | 0 | 0 | reference resolver |
| REFERENCE_RESOLUTION | WRONG_ENTITY_TYPE | 0 | 0 | 0 | semantic compatibility |
| ATTRIBUTE_ATTACHMENT | DOSE_ATTACHMENT | 0 | 0 | 0 | attribute ownership |
| ATTRIBUTE_ATTACHMENT | FREQUENCY_ATTACHMENT | 0 | 0 | 0 | attribute ownership |
| ATTRIBUTE_ATTACHMENT | STATUS_ATTACHMENT | 1 | 1 | 1 | attachment/state |
| ATTRIBUTE_ATTACHMENT | TEMPORAL_ATTACHMENT | 3 | 3 | 3 | attachment/lifetime |
| ATTRIBUTE_ATTACHMENT | NEGATION_ATTACHMENT | 0 | 0 | 0 | local scope |
| ATTRIBUTE_ATTACHMENT | LATERALITY_ATTACHMENT | 0 | 0 | 0 | local scope |
| ATTRIBUTE_ATTACHMENT | EXPERIENCER_ATTACHMENT | 0 | 0 | 0 | experiencer projection |
| RELATION_RESOLUTION | MISSING_RELATION | 3 | 3 | 3 | relation resolver |
| RELATION_RESOLUTION | WRONG_RELATION | 0 | 0 | 0 | relation resolver |
| RELATION_RESOLUTION | WRONG_RELATION_SOURCE | 0 | 0 | 0 | relation provenance |
| RELATION_RESOLUTION | WRONG_RELATION_TARGET | 0 | 0 | 0 | relation ownership |
| SPEAKER_ATTRIBUTION | SPEAKER_MISMATCH | 0 | 0 | 0 | speaker policy |
| SPEAKER_ATTRIBUTION | EXPERIENCER_MISMATCH | 0 | 0 | 0 | experiencer policy |
| PROVENANCE | PROVENANCE_MISMATCH | 4 | 4 | 4 | field-level provenance |

## Representative examples

- `v6-c-002-1`, `v6-c-002-2`, `v6-c-002-3`: the family mention remains temporally attached to the wrong turn after V1.
- `sim-v6-0051`: status ownership remains incorrect for the new symptom even though laterality is preserved.
- `sim-v6-0049`, `sim-v6-0054`, `sim-v6-0055`: continuity attributes improve, but required relation projection remains incomplete.

Conclusion: the residuals justify typed state, explicit ownership, relation-first projection and an ambiguity/lifetime policy. No algorithmic tuning was performed before this analysis.
