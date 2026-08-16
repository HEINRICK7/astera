# A1/A2 Boundary Validation & Repair Plan — V6

Status: **HUMAN GATE — ANALYSIS ONLY**  
Policy: `CLINICAL_SEMANTIC_POLICY` v1.1  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`  
Resolver, corpus, gold, policy, and benchmark changes: **none**

## Method

Each Type-A finding was traced against the available candidate, context, ownership, relation, resolved-semantics, and projection provenance. A downstream relation finding was marked causally dependent only when the same mention also contained an upstream attribute/status/transition divergence. Otherwise it remains an independent relation finding.

## Current versus validated class

| Class | Current | Validated |
|---|---:|---:|
| A1 | 103 | 95 |
| A2 | 21 | 29 |
| A3 | 0 | 0 |
| A4 | 0 | 0 |

The causal validation does not justify collapsing all A2 into A1. It confirms a narrower set of downstream dependencies and keeps the remaining A2 boundaries explicit.

## First divergence stages

| Stage | Findings | Interpretation |
|---|---:|---|
| ResolvedClinicalSemantics | 42 | first observed divergence in the trace |
| Attribute Ownership | 32 | first observed divergence in the trace |
| Cross-Segment Resolution | 28 | first observed divergence in the trace |
| Local Semantics | 17 | first observed divergence in the trace |
| Relation Resolution | 5 | first observed divergence in the trace |

## Validated causal relations

| Upstream root | Downstream root | Findings | Evidence rule |
|---|---|---:|---|
| ROOT-ATTRIBUTE-OWNERSHIP | ROOT-RELATION-RESOLUTION | 8 | same mention has upstream field divergence and downstream relation finding |
| ROOT-TRANSITION-OWNERSHIP | ROOT-RELATION-RESOLUTION | 10 | same mention has upstream field divergence and downstream relation finding |

## Interpretation

- The strongest validated dependencies are relation findings downstream of same-mention attribute/transition/status divergences.
- A relation appearing downstream in the score is not automatically an independent relation-resolver defect.
- The available trace does not prove an A3 unresolved outcome or an A4 deterministic-rule ceiling; both remain zero without being treated as impossible.
- Mention extraction and broad reference-resolution limitations remain unassessed by this query-per-gold evidence.

## Repair V5 boundary

Repair V5 is **NOT AUTHORIZED**. The causal graph must first receive human approval, and any future repair must be staged by upstream root cause with invariant tests between stages.

```text
V6 frozen              = yes
policy v1.1 frozen     = yes
Type B untouched       = yes
holdouts               = NOT_EXECUTED
V7                    = BLOCKED
Shadow                = BLOCKED
Production            = BLOCKED
Repair V5              = NOT AUTHORIZED
```
