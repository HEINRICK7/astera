# V6 Semantic Policy Failure Analysis

V4 removed a substantial Type-A portion of the mismatch, but the frozen V6 gate remains unmet. The post-V4 audit reports:

- 78 records with divergence;
- 85 field/relation findings;
- 27 remaining Type-A findings;
- 58 Type-C policy/interpretation findings;
- 0 proven Type-B gold errors;
- 44 gold-review queue items.

The dominant remaining cluster is still `status=present` versus the resolver's `status=null` for current symptom assertions. Other unresolved clusters include the `DISCONTINUED_AT` relation vocabulary and temporal policy for event time versus assertion time.

These are policy decisions, not safe automatic resolver repairs. The next action requires human approval of [CLINICAL_SEMANTIC_POLICY.md](/home/carlos-henrique/Documentos/workspace/astera/docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md), followed by a separately controlled policy-alignment milestone.

No gold annotation was changed. No holdout was executed. V7, Shadow Integration, and production remain blocked.
