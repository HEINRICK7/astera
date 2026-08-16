# Post-V4 Type A Strategy & Error Decomposition

Status: **HUMAN GATE — ANALYSIS ONLY**  
Policy: `CLINICAL_SEMANTIC_POLICY` v1.1  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`  
Resolver/corpus/gold/policy changes during analysis: **none**

## Snapshot

The adjudicated snapshot contains **124 Type A findings**, across **59 cases** and **82 affected mentions**.

| Repair class | Count | Interpretation |
|---|---:|---|
| A1 | 103 | Local/deterministic bug |
| A2 | 21 | Architectural/integration boundary |
| A3 | 0 | Should remain unresolved |
| A4 | 0 | Probable deterministic-rule limit |

## Primary dimension matrix

Counts are mutually exclusive primary dimensions. Cross-segment is also reported as an overlapping overlay.

| Dimension | Count | Cases | Mentions | Relations | Policy | Repair class | Risk |
|---|---:|---:|---:|---:|---|---|---|
| STATUS | 37 | 26 | 37 | 0 | `SEM-STATUS-001` | A1 | medium |
| MENTION_SCOPE | 22 | 18 | 22 | 0 | `SEM-NEG-001` | A1 | medium |
| TEMPORALITY | 11 | 11 | 11 | 0 | `SEM-TEMP-001` | A1 | high |
| RELATION_MISSING | 10 | 10 | 10 | 10 | `SEM-REL-001` | A2 | high |
| ATTRIBUTE_OWNERSHIP | 8 | 8 | 8 | 0 | `SEM-REL-001` | A1 | medium |
| CROSS_SEGMENT | 6 | 3 | 6 | 0 | `SEM-XSEG-001` | A2 | high |
| RELATION_MISSING | 5 | 5 | 5 | 5 | `SEM-REL-001` | A2 | high |
| STATUS | 5 | 5 | 5 | 0 | `SEM-STATUS-001` | A1 | medium |
| RELATION_WRONG | 4 | 3 | 3 | 4 | `SEM-REL-002` | A1 | high |
| RELATION_WRONG | 4 | 3 | 3 | 4 | `SEM-REL-002` | A1 | high |
| NEGATION | 3 | 3 | 3 | 0 | `SEM-NEG-001` | A1 | medium |
| TEMPORALITY | 3 | 3 | 3 | 0 | `SEM-TEMP-001` | A1 | high |
| DOSE | 2 | 1 | 1 | 0 | `SEM-DOSE-001` | A1 | high |
| FREQUENCY | 2 | 2 | 2 | 0 | `SEM-FREQ-001` | A1 | high |
| EXPERIENCER | 1 | 1 | 1 | 0 | `SEM-EXP-001` | A1 | medium |
| FREQUENCY | 1 | 1 | 1 | 0 | `SEM-FREQ-001` | A1 | high |

## Top root causes

1. **37** — gold uses present status while the resolver contract represents current assertion as null
2. **22** — negation cue appears scoped to another mention; target ownership/scope is wrong
3. **14** — gold relation was not present in resolved projection
4. **11** — historical-event cue conflicts with the resolved current temporality
5. **8** — explicit laterality cue was not attached to the target mention

## Cross-segment overlay

102 findings affect 40 cases and 60 mentions through cross-segment provenance. This is an overlapping diagnostic dimension, not an additional bucket.

## Interpretation

- A1 dominates the current decomposition: explicit cue, ownership, transition, and relation-admissibility defects appear deterministic under policy v1.1.
- A2 is concentrated in cross-segment state inheritance and relation emission/projection boundaries; it should not be addressed by adding isolated lexical rules.
- A3 and A4 have no findings in this Type-A snapshot. This is not evidence that the deterministic engine has no ceiling; it means the current Type-A set does not prove those classes.
- Mention extraction and reference resolution have no independently measured Type-A findings in this query-per-gold trace; they remain unassessed rather than zero in the broader system.

## Recommendation and gate

Recommended next milestone: human review of the A1/A2 boundary followed by a narrowly scoped Type-A repair proposal. Do not start Repair V5 or add a probabilistic provider from this report alone.

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
