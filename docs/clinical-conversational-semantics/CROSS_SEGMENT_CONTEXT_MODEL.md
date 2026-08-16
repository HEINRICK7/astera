# Cross-Segment Context Model

`CrossSegmentContextState` is a derived immutable snapshot. It preserves candidate mention identity, entity type, speaker, experiencer, segment, turn, status, recency, confidence and source segment IDs.

State is grouped by semantic role rather than a single `last_mention` pointer. A topic switch does not erase evidence; it changes candidate eligibility through `ContextLifetimePolicy`. A state snapshot never replaces the segment evidence that produced it.

Required test coverage is present for multiple medications, multiple symptoms, speaker changes, family/patient separation, topic changes and stale context. The engineering-only fixture is marked `engineering_regression_only=true` and `generalization_evidence=false`.
