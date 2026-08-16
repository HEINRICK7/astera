# V5 Generalization Corpus

The v5 corpus is frozen and contains 120 new PT-BR cases and 207 mentions.
Its texts are disjoint from v3 and v4 and cover colloquial wording, STT-like
phrasing, abbreviated clinical language, multi-medication changes, mixed
family/patient history, partial negation, conflicting temporal cues and
multi-mention laterality.

The first frozen-code run used the repaired v4 code without semantic changes:

| Metric | V5 initial | Gate |
|---|---:|---:|
| mention_exact_match | 0.657 | >= 0.90 |
| relation_exact_match | 0.802 | >= 0.95 |
| scope_accuracy | 0.936 | >= 0.97 |
| cross_mention_isolation | 0.473 | >= 0.95 |
| provenance | 1.000 | = 1.00 |

The gate failed as expected for a generalization corpus. The dominant error
classes were `MULTI_MENTION_COLLISION` (39 cases), `DOSE_ATTACHMENT` (32),
`TEMPORAL_SCOPE` (26), `NEGATION_SCOPE` (19) and `STATUS_CONFLICT` (12).

## V5 Composition Repair

The corpus remained byte-for-byte frozen. Repair focused on mention ownership
and explicit local composition: coordinated negation scope, medication restart
precedence, dose/frequency attachment, temporal ownership, family-versus-
patient experiencer scope and status relevance. No provider was promoted to
the Runtime.

The repaired run passed all gates:

| Metric | V5 repaired | Gate |
|---|---:|---:|
| mention_exact_match | 1.000 | >= 0.90 |
| relation_exact_match | 1.000 | >= 0.95 |
| scope_accuracy | 1.000 | >= 0.97 |
| cross_mention_isolation | 1.000 | >= 0.95 |
| provenance | 1.000 | = 1.00 |

The result is laboratory evidence of compositional correctness on v5, not
generalization proof for unseen data. Shadow Integration and production
promotion remain blocked until v6 unseen validation and the subsequent shadow
stage.
