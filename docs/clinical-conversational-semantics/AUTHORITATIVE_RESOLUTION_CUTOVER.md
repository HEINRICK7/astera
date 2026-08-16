# Authoritative Reference & Attribute Ownership Cutover

Status: **FAIL — HUMAN GATE**. Holdout evaluation: `NOT_EXECUTED`.

## Contract

Cross-segment semantics now pass through:

`ClinicalSemanticCandidate → ResolvedClinicalSemantics → AuthoritativeProjectionWriter → ClinicalContextResult`

`ResolvedClinicalSemantics` owns resolved attributes and unique relations. It preserves explicit `UNRESOLVED` and `AMBIGUOUS` statuses and refuses missing critical fields. Local behavior remains unchanged when no conversational context is present.

## Authority measurements

| Measurement | Result |
|---|---:|
| resolver decisions total | 2728 |
| resolver decisions preserved | 2644 |
| resolver decisions overwritten from local candidate | 84 |
| legacy fallback count | 0 |
| ambiguous forced resolution count | 0 |

The 84 overwritten decisions are intentional context-resolution changes, not downstream losses. The absence of fallback confirms that the final result came from the authoritative writer.

## V6 comparison

| Metric | Blind | Repair V1 | Repair V2 | Authoritative Cutover |
|---|---:|---:|---:|---:|
| mention exact | 0.7216 | 0.7695 | 0.7754 | 0.7754 |
| relation exact | 0.7442 | 0.7442 | 0.8140 | 0.8140 |
| cross-mention isolation | 0.5766 | 0.6204 | 0.6204 | 0.6204 |
| cross-segment resolution | 0.4597 | 0.5887 | 0.6048 | 0.6048 |
| provenance | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

Conclusion: authority composition is now explicit and verified, but it does not by itself close the metric gap. The remaining problem is candidate quality/ownership resolution, not a post-resolution legacy overwrite. Stop here and require a new HUMAN GATE before further repair work.
