# Resolved Semantics Preservation & Projection Integrity

Date: 2026-08-15  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

The real V6 path was traced as:

```text
candidate → resolved → projection writer → evaluated result → V6 comparison
```

## Integrity gate

| Metric | Result |
|---|---:|
| projection preservation rate | 1.0000 |
| relation preservation rate | 1.0000 |
| ownership preservation rate | 1.0000 |
| evaluation preservation rate | 1.0000 |
| provenance | 1.0000 |

No resolved attribute was changed or dropped by the writer. No resolved relation was dropped or rewritten between `ResolvedClinicalSemantics` and `ClinicalContextResult`. The end-to-end trace also found no projected-to-evaluated attribute loss.

## The 162 overwrite signal

The V3 authority counter accumulated across repeated harness passes. The trace found 54 unique local-to-resolved field changes. V3 reported 162 overwrites, giving a repetition factor of 3.0. These are resolution changes preserved by projection, not 162 independent writer losses.

## Where the V6 errors remain

The remaining mismatches are before projection or between resolved semantics and gold semantics:

- 84 field-level `RESOLUTION_VS_GOLD_MISMATCH` observations;
- 16 `RESOLUTION_VS_GOLD_RELATION_MISMATCH` observations;
- no semantic relation loss between projection and evaluation after matching the production evidence namespace.

The candidate gate is explicitly an engineering fixture gate, not a full V6 semantic-accuracy gate. The real V6 trace closes that evaluation gap without changing candidate generation.

The machine-readable trace is [projection-integrity-audit-final-v2-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/projection-integrity-audit-final-v2-2026-08-15.json). It contains stage values and diffs for every problematic V6 target.

No projection repair was applied because the projection integrity gate passed.
