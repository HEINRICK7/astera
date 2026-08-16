# Clinical Conversational Semantics

Status: **LAB architecture — V2 gate failed; not production**.

The intended pipeline is:

`Canonical Evidence → Local Segment Semantics → CrossSegmentContextState → Reference Resolution → Attribute Attachment → Relation Resolution → ClinicalMentionProjection → Clinical Context`

Speech is not clinical semantics. The Transcriber produces audio → text. This layer consumes text/segments and derives context, mentions and relations without rewriting evidence.

The current lab composition is:

- `CrossSegmentContextState`: immutable, typed candidate state grouped by medication, symptom, condition, procedure, family, temporal and discourse contexts.
- `ClinicalReferenceResolver`: deterministic candidate scoring using semantic compatibility, speaker, experiencer, distance, recency and clinical attribute compatibility.
- `ClinicalAttributeAttachmentResolver`: field-level ownership and provenance.
- `ClinicalRelationResolver`: first-class relation projection using the existing domain vocabulary.
- `ContextLifetimePolicy`: validity based on turn distance, speaker/topic changes and entity compatibility; no arbitrary timeout.
- `AmbiguityPolicy`: `RESOLVED`, `AMBIGUOUS`, `UNRESOLVED`.
- `ConversationalSemanticsTrace`: LAB-only explanation object; no PHI logging contract.

The adapter remains a compatibility façade around these derived structures. It does not mutate Raw Evidence, Canonical Evidence or the official corpus.
