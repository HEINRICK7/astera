# Reference Resolution

`ClinicalReferenceResolver` emits ranked `ReferenceCandidate` values and a resolution status. It does not concatenate text and does not know V6 case IDs.

Scoring inputs are semantic compatibility, speaker compatibility, discourse distance, recency, experiencer and requested clinical attributes. A close score tie is `AMBIGUOUS`; no compatible antecedent is `UNRESOLVED`. Neither state is converted into an invented relation.

The V2 integration exposes candidates and scores through `ConversationalSemanticsTrace`. The next repair must make this decision authoritative before any cross-turn attribute is attached.
