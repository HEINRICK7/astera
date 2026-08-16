# Post-Holdout Generalization Repair — Final Report

## Gate decision

The post-holdout repair passed its internal engineering gate and the new
unseen holdout-v2 passed exactly once. The consumed holdouts
`sim-v6-0056`–`0058` were not rerun, tuned, or used for approval.

## Repair scope

- Resolved laterality, dose, frequency, and route now receive complete relation materialization when their owned values arrive through continuity.
- Current medication state is kept `current` when a historical cue belongs to a dose-change event; the event time is preserved separately as `event_temporality`.
- Authoritative projection now restores full-conversation provenance with explicit `source_scope=conversation` and target segment identity.
- Explicit current medication changes such as `passei para` and `ajustei para` are treated as general active-state cues.

No new provider, LLM, policy change, corpus change, or old-holdout rerun was introduced.

## Internal gate

| Metric | Result | Gate |
|---|---:|---:|
| relation materialization rate | 1.0000 | 1.0000 |
| temporal ownership accuracy | 1.0000 | 1.0000 |
| provenance contract rate | 1.0000 | 1.0000 |

Engineering suite: `32 passed`.

## New unseen holdout-v2

The new set contains 6 reviewed cases and was executed once after the repair
freeze. It is independent from the consumed holdouts and covers laterality,
dose, event/state temporality, family experiencer, medication status,
frequency, relation provenance, and attribute provenance.

| Metric | Result |
|---|---:|
| mention exact match | 1.0000 |
| relation exact match | 1.0000 |
| cross-segment resolution | 1.0000 |
| attribute ownership | 1.0000 |
| provenance contract | 1.0000 |
| temporal ownership | 1.0000 |
| status | 1.0000 |
| temporality | 1.0000 |
| experiencer | 1.0000 |
| laterality | 1.0000 |
| dose | 1.0000 |
| frequency | 1.0000 |

## State after evaluation

- V6 policy-aligned: `PASS`
- Old holdouts: `FAIL / CONSUMED / HISTORICAL`
- Post-holdout repair: `PASS / FROZEN`
- New holdout-v2: `PASS / CONSUMED`
- V7 Foundation: `ELIGIBLE`
- Shadow Integration: `BLOCKED`
- Production: `BLOCKED`

The new holdout-v2 is now also consumed evidence and must not be reused as a
future generalization proof. Any future V7 validation requires another unseen
set.
