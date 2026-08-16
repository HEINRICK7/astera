# Relation Writer Inventory

Status: **HUMAN GATE — inventory only**

The inventory is static and was produced without executing the resolver.

- relation writer sites: `6`
- competing relation-producing/mutating components: `5`
- relation rehydration boundary: `cross_segment_context.py:154-167`
- duplicated/competing vocabulary observed: `HAS_DOSE`, `HAS_FREQUENCY`, `HAS_LATERALITY`, `DISCONTINUED_AT`, `CHANGED_FROM`

| ID | Component | Classification | Operation | Mutation |
|---|---|---|---|---|
| RW-01 | `labs/terminology_benchmark/context_safety.py:387-405` / local semantics | LOCAL_CANDIDATE_PRODUCER | creates initial HAS_DOSE/HAS_FREQUENCY/HAS_ROUTE/HAS_LATERALITY/DISCONTINUED_AT projection relations | creates |
| RW-02 | `labs/terminology_benchmark/clinical_conversational_semantics.py:747-814` / ClinicalRelationResolver | CONTEXT_RESOLVER | compiles attribute attachments, CHANGED_FROM and REFERS_TO; includes HAS_STATUS/EXPERIENCER_OF | creates |
| RW-03 | `labs/terminology_benchmark/cross_segment_context.py:178-191` / cross-segment resolver | CONTEXT_RESOLVER | synthesizes DISCONTINUED_AT when status is discontinued | creates |
| RW-04 | `labs/terminology_benchmark/cross_segment_context.py:841-976` / transition resolver seam | CONTEXT_RESOLVER | calls ClinicalRelationResolver and appends transition relations into provenance['projection']['relations'] | creates and mutates |
| RW-05 | `labs/terminology_benchmark/clinical_projection.py:53-175` / ClinicalRelationMaterializer | PROJECTION_WRITER | normalizes, suppresses stale relations, deduplicates and derives current attribute relations | creates, suppresses and rewrites |
| RW-06 | `labs/terminology_benchmark/clinical_conversational_semantics.py:178-257` / AuthoritativeProjectionWriter | PROJECTION_WRITER | replaces final result fields and serializes resolved_relations into final projection | materializes final set |

## Architectural observations

1. Local projection creates relations before context resolution has authoritative ownership.
2. Transition handling invokes a second relation resolver and mutates the projection list after local output.
3. Cross-segment status handling has a dedicated relation creation path.
4. ClinicalRelationMaterializer both suppresses and reconstructs relations, while AuthoritativeProjectionWriter serializes another relation set.
5. Provenance can be rewritten at the materializer boundary, so relation source ownership is not established once at a single compiler boundary.

Conclusion: the current system has multiple relation authorities and post-resolution mutation points. This supports evaluating R2, but does not by itself prove that upstream reference/state errors disappear.
