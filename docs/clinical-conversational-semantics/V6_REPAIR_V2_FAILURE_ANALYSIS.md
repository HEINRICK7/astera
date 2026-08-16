# V6 Repair V2 — Failure Analysis

Status: **FAIL — HUMAN GATE**. Holdout evaluation: **NOT_EXECUTED**.

## Frozen input

- Official corpus checksum before and after: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`.
- V6 corpus was not modified.
- Raw Evidence and Canonical Evidence were not modified.
- Shadow Integration: `BLOCKED`.
- Production promotion: `BLOCKED`.

## Baseline / V1 / V2

| Metric | Blind | V1 | V2 | Gate |
|---|---:|---:|---:|---:|
| mention exact | 0.7216 | 0.7695 | 0.7754 | >= 0.90 |
| relation exact | 0.7442 | 0.7442 | 0.8140 | >= 0.95 |
| scope accuracy | 0.9635 | 0.9743 | 0.9671 | — |
| cross-mention isolation | 0.5766 | 0.6204 | 0.6204 | >= 0.95 |
| cross-segment resolution | 0.4597 | 0.5887 | 0.6048 | >= 0.90 |
| speaker | 0.9677 | 0.9919 | 0.9919 | — |
| provenance | 1.0000 | 1.0000 | 1.0000 | = 1.00 |

Improved cases: 14. Regressed cases: 0. Newly broken cases: 0.

## Diagnosis

1. Relation projection is materially better but incomplete. Dose/frequency transitions now produce explicit `CHANGED_FROM`, `HAS_DOSE` and `HAS_FREQUENCY` relations in the cases they can prove; discontinuation and cross-turn relation ownership still lack complete projection.
2. Mention exactness remains below gate because the local deterministic adapter cannot identify every unseen entity form; the cross-segment layer must not invent concepts to compensate.
3. Cross-segment resolution remains below gate because the legacy continuity application still has paths that apply attributes without a fully resolved antecedent/ownership decision.
4. Provenance remains 1.000, but field-level provenance needs stronger assertions in future repairs.

## Recommended next design

- Make the typed `ClinicalReferenceResolver` decision authoritative for cross-turn attachment.
- Make `ClinicalAttributeAttachmentResolver` the only path allowed to copy a field across segments.
- Add explicit relation projection for `HAS_STATUS`, `DISCONTINUED_AT`, `REFERS_TO`, `CHANGED_TO` and `EXPERIENCER_OF` where the current contract requires them.
- Keep unresolved and ambiguous candidates as trace data; do not force a relation.
- Repeat V6 Repair V2 only after a new repair version and new targeted tests. Do not run holdouts from this state.
