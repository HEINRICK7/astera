# V4 Composition Repair

The v4 corpus remained unchanged during repair: 100 cases and 134 mentions.

| Metric | Initial v4 | Repaired v4 | Gate |
|---|---:|---:|---:|
| mention_exact_match | 0.575 | 0.993 | >= 0.85 |
| relation_exact_match | 0.833 | 1.000 | >= 0.90 |
| scope_accuracy | 0.949 | 1.000 | >= 0.95 |
| cross_mention_isolation | 0.588 | 0.971 | >= 0.90 |
| provenance | 1.000 | 1.000 | = 1.00 |

The repair introduced mention-local relation projections for dose, frequency,
route, laterality and discontinuation, plus boundary-aware span resolution.
It also repaired local scope for negation, temporal cues, experiencer,
medication changes and multi-mention attachment.

One gold annotation remains inconsistent with its text: `v4-074` contains
“à tarde” for hidroclorotiazida but does not annotate frequency. The adapter
keeps the semantically supported frequency instead of distorting the rule.

The experimental gate passes. `production_promotion` remains false and Shadow
Integration remains blocked pending an unseen v5 corpus.
