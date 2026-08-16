# Antecedent Ranking V2

Antecedent ranking is deterministic and explainable. Each eligible candidate is scored from:

- semantic compatibility;
- entity-type compatibility;
- discourse distance and recency;
- speaker compatibility;
- requested clinical-attribute compatibility;
- explicit-reference strength;
- topic continuity;
- candidate confidence;
- stale-context penalty.

The resolver filters candidates through `ContextLifetimePolicy`, sorts by score, and applies `AmbiguityPolicy`. A score below the minimum is `UNRESOLVED`; a tie inside the configured margin is `AMBIGUOUS`; neither state selects an antecedent.

The trace records candidate IDs, scores, ranking order, selected owner, rejected candidates, and the resolution status. This makes later overwrite/ignore analysis possible without logging source phrases.
