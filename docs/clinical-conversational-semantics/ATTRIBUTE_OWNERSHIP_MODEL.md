# Attribute Ownership Model

Attributes are candidates until a compatible clinical mention owns them. The ownership resolver applies three constraints in order:

1. Candidate-declared compatible entity types, or the general `ATTRIBUTE_OWNER_TYPES` policy when the candidate does not declare them.
2. Explicit candidate owner IDs, when present.
3. One-owner materialization: a resolved attribute is attached to one mention only.

Examples:

| Attribute | Compatible owners |
|---|---|
| dose, frequency, route | medication, treatment |
| laterality | symptom, condition, anatomical |
| negated, temporality, experiencer | mention-compatible clinical entities |
| status | medication, treatment, symptom, condition, procedure |

An incompatible candidate becomes `UNRESOLVED`; it is never silently attached to a nearby mention. `ClinicalRelationResolver` projects only resolved attachments and includes source/target mention IDs plus source segment provenance.

The model is implemented in `clinical_conversational_semantics.py` and exercised by the ownership and endpoint regression tests.
