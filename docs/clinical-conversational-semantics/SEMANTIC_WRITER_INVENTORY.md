# Semantic Writer Inventory — Authoritative Cutover

Status: **DONE — audit executed**.

Automated source: `labs/terminology_benchmark/semantic_writer_audit.py`. Machine-readable output: `labs/terminology_benchmark/results/semantic-writer-inventory-2026-08-15.json`.

The audit scans the LAB semantic modules and runtime clinical contracts for writes involving negation, temporality, experiencer, laterality, dose, frequency, route and status. The raw AST inventory contains 274 matched write sites; generic declarations are retained for traceability.

## Semantic writers

| Writer | Classification | Authority after cutover |
|---|---|---|
| `NieDEPtBrSafetyRules.analyze` | `LOCAL_CANDIDATE_PRODUCER` | produces local candidate only on cross-segment path |
| `CrossSegmentContextResolver._apply_continuity` | `CONTEXT_RESOLVER` | produces contextual candidate state; does not return final projection |
| `AuthoritativeProjectionWriter.materialize` | `PROJECTION_WRITER` | sole final writer for cross-segment results |
| `ClinicalMentionProjection.to_provenance` | `PROJECTION_WRITER` | serialization only; no semantic decision |
| `HybridClinicalContextAdapter` | `LEGACY_OVERRIDE` | outside authoritative cross-segment path; must not be wired into cutover |
| `DeterministicContextAdapter` / optional providers | `LOCAL_CANDIDATE_PRODUCER` | local-only behavior |

The raw audit found 10 legacy-override matches, all in optional/local adapter code. The cross-segment façade is covered by an integration test asserting that its returned result has `semantic_role=PROJECTION_WRITER` and `legacy_fallback_count=0`.

## Authority rule

`LOCAL_CANDIDATE_PRODUCER → CONTEXT_RESOLVER → PROJECTION_WRITER`

No local result is applied after the projection writer returns. Missing resolved fields raise an error instead of silently falling back.
