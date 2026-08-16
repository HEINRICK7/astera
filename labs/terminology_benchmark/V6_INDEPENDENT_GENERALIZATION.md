# V6 Independent Generalization

Status: official V6 frozen; first blind run and error taxonomy recorded.
Shadow Integration and production promotion remain blocked.

The draft contains 105 cases and 255 mentions:

- 60 independent adversarial cases;
- 30 realistic spontaneous/STT-like cases;
- 15 conversational multi-segment cases.

The 14 simulator candidates remain separate and `PENDING_REVIEW`. They are
not part of the V6 draft and cannot be promoted automatically.

## Assembly rule

The planned official composition is 150 cases:

```text
60 independent
45 realistic/conversational
45 simulator-approved
```

The assembler validates source proportions, duplicate IDs/text, prior-corpus
disjunction, segment ownership and segment-level provenance. Every
conversational gold must identify the segment that supports the mention and
must record the source segment for each annotated attribute/relation. It fails explicitly while the 45
simulator-approved cases are missing. No official
`pt_br_clinical_semantics_v6.jsonl` is created yet.

## Human-review boundary

Simulator candidates remain review records, not gold annotations. A reviewer
must explicitly provide:

- a named reviewer and review notes;
- a gold mention with source segment ownership;
- attribute provenance, including the concept source segment;
- relation provenance for status, temporal, negation, experiencer, dose and
  other relation-bearing attributes.

The review helper can materialize an approved candidate as a
`simulator-approved` `BenchmarkCase`, but it does not write the official V6
file or bypass the composition quota. The current 14 candidates are still
`PENDING_REVIEW`, so this gate remains closed.

A read-only review packet is available through
`run_v6_review_queue`. It displays candidate text, historical origin, error
taxonomy and provenance while leaving mentions, relations and approval empty
for the human reviewer.

To create the editable worksheet:

```bash
.venv/bin/python -m labs.terminology_benchmark.run_v6_review_queue \
  --output labs/terminology_benchmark/results/v6-human-review-2026-08-15.json
```

After filling decisions and golds, validate it with
`run_v6_review_validation`. Validation is still not assembly and never writes
the official corpus.

## Human review submission

The first authorized human review was materialized in
`results/v6-human-review-submission-2026-08-15.json` and validated with
`run_v6_review_validation`:

```text
APPROVED:          11
REJECTED:           3
PENDING_REVIEW:     0
approved mentions: 20
provenance:       valid
official corpus:  not created
```

The rejected cases remain empty by design because their medication identity or
experiencer cannot be established without inference. The planned official
composition requires 45 `simulator-approved` cases; 34 additional reviewed
cases are still required. Freeze and the blind run remain blocked.

## Simulator expansion

The expansion batch was generated with IDs `sim-v6-0015` through
`sim-v6-0054`:

```text
new candidates:       40
cross-segment cases:   6
gold:                  none
review status:         PENDING_REVIEW
prior/draft overlap:   none
official mutation:     false
```

Its review worksheet is
`results/v6-human-review-expansion-2026-08-15.json`. These candidates must
follow the same human-review and provenance validation process. They do not
complete the quota until approved; no candidate was approved automatically.

The reviewed submission was validated after correcting only
`sim-v6-0050.surface` from `câncer de mama` to the continuous source span
`câncer`:

```text
new APPROVED:       33
new REJECTED:        7
new PENDING:         0
new mentions:       58
provenance:       valid
total approved:     44
quota remaining:     1
```

The materialized submission is
`results/v6-human-review-expansion-submission-2026-08-15.json`. The V6
official corpus remains unfrozen.

## Micro-expansion for the final quota gap

Four additional cross-segment candidates were generated as
`sim-v6-0055` through `sim-v6-0058`. They are all gold-free and
`PENDING_REVIEW` in
`results/clinical-language-simulator-v6-micro-expansion-2026-08-15.jsonl`.
The review worksheet is
`results/v6-human-review-micro-expansion-2026-08-15.json`. One valid human
approval is sufficient to reach the quota of 45.

The human review approved all four candidates. The materialized submission is
`results/v6-human-review-micro-expansion-submission-2026-08-15.json`:

```text
previous approved: 44
micro approved:     4
total approved:    48
planned quota:      45
```

The official freeze used the pre-registered quota of exactly 45 simulator-
approved cases. Selection was deterministic and performance-blind: the first
approved candidates in stable `candidate_id` order were selected until the
quota was reached. `sim-v6-0055` was selected; `sim-v6-0056` through
`sim-v6-0058` remain approved reserve/holdout cases.

The freeze manifest records 48 approved cases, 45 official cases and 3
reserve cases, together with input and corpus checksums.

## Official freeze

The official corpus is now frozen:

```text
cases:              150
mentions:           334
independent:         60
realistic:           45
simulator-approved:  45
official checksum:   1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10
```

Artifacts:

- `data/pt_br_clinical_semantics_v6.jsonl`
- `results/v6-official-freeze-manifest-2026-08-15.json`

## First blind run

The implementation was not changed for this run. The first blind run was
executed exactly once against the frozen official corpus. No semantic repair
was applied:

| Metric | Blind result | Gate |
|---|---:|---:|
| mention_exact_match | 0.722 | >= 0.90 |
| relation_exact_match | 0.744 | >= 0.95 |
| scope_accuracy | 0.963 | >= 0.97 |
| cross_mention_isolation | 0.577 | >= 0.95 |
| cross_segment_resolution | 0.460 | >= 0.90 |
| speaker_attribution | 0.968 | >= 0.95 |
| provenance | 1.000 | = 1.00 |

The blind run failed the gate. The most important signals are status,
mention composition, multi-mention isolation and cross-segment resolution.
This is a validation result, not a production decision.

The post-blind taxonomy was generated separately, without repair:

- `results/context-taxonomy-v6-blind-2026-08-15.json`
- dominant classes: `MULTI_MENTION_COLLISION` (58), `STATUS_CONFLICT` (46),
  `TEMPORAL_SCOPE` (29), `NEGATION_SCOPE` (20)

Artifacts:

- `data/pt_br_clinical_semantics_v6_draft.jsonl`
- `results/context-validation-v6-blind-2026-08-15.json`
- `results/v6-official-freeze-manifest-2026-08-15.json`

No repair was started in this milestone. The next milestone may analyze the
taxonomy and propose a repair, but must preserve the frozen V6 corpus and the
raw blind result.
