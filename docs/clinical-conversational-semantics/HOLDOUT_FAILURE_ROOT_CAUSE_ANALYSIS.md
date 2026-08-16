# Holdout Failure Root Cause Analysis — Generalization Gap

> Status: HUMAN GATE. This is a post-holdout diagnosis only; no resolver repair was authorized or performed.

## Integrity boundary

The three cases were executed once and are now consumed holdouts. This report reads the persisted one-shot result and frozen source, then reconstructs the causal path from static code evidence. It does not call the resolver, rerun a holdout, or modify resolver, policy, corpus, gold, or the holdout source.

- `consumed_holdout = true`
- `generalization_evidence = historical`
- `holdout_rerun = false`
- V6, resolver freeze, and Semantic Policy v1.2 preserved
- Repair after holdout: `NOT_AUTHORIZED`
- V7, Shadow Integration, and Production: `BLOCKED`

## Diagnosis

The semantic failures are 3: 3 are classified as `GENERALIZATION_BUG`, and no `GENERALIZATION_CAPABILITY_GAP` is proven. The system found the relevant antecedents and values; the unseen-path failures occur after candidate/reference success, in relation materialization and temporal ownership.

| Finding | First divergence | Classification | Generalization class | Confidence |
|---|---|---|---|---|
| 0057-F1 (sim-v6-0057) | Relation Resolution | `RELATION_NOT_GENERATED` | `GENERALIZATION_BUG` | high |
| 0058-F1 (sim-v6-0058) | Relation Resolution | `RELATION_NOT_GENERATED` | `GENERALIZATION_BUG` | high |
| 0058-F2 (sim-v6-0058) | Cross-Segment Resolution | `TEMPORAL_OWNERSHIP_FAILURE` | `GENERALIZATION_BUG` | high |

### Classification counts

| Class | Count |
|---|---:|
| `CANDIDATE_MISSING` | 0 |
| `ATTRIBUTE_NOT_PROPAGATED` | 0 |
| `RELATION_NOT_GENERATED` | 2 |
| `RELATION_FILTERED` | 0 |
| `CROSS_SEGMENT_REFERENCE_FAILURE` | 0 |
| `TEMPORAL_OWNERSHIP_FAILURE` | 1 |
| `PROVENANCE_MATERIALIZATION_FAILURE` | 0 |
| `POLICY_MISMATCH` | 0 |

## Case traces

### sim-v6-0056

`Médico: Alguém da família tem diabetes?
Paciente: Minha irmã tem.`

**Segments**

- `sim-v6-0056:segment-01` (clinician): Alguém da família tem diabetes?
- `sim-v6-0056:segment-02` (patient): Minha irmã tem.

- Local mentions: `[{"surface": "diabetes", "concept_id": "condition.diabetes", "segment_id": "sim-v6-0056:segment-01"}]`
- Candidate attributes: `[{"field": "experiencer", "value": "family", "source_segment_id": "sim-v6-0056:segment-02", "rule": "family continuity"}, {"field": "temporality", "value": "current", "source_segment_id": "sim-v6-0056:segment-02", "rule": "current assertion"}]`
- Selected antecedent: `{"antecedent": "diabetes", "segment_id": "sim-v6-0056:segment-01", "status": "selected"}`
- Resolved attributes: `{"negated": false, "certainty": "confirmed", "temporality": "current", "experiencer": "family", "laterality": null, "dose": null, "dose_value": null, "dose_unit": null, "frequency": null, "route": null, "status": null}`
- Resolved/projected relations: `[]`
- Expected: `{"fields": {"negated": false, "certainty": "confirmed", "temporality": "current", "experiencer": "family", "laterality": null, "dose": null, "dose_value": null, "dose_unit": null, "frequency": null, "route": null, "status": null}, "relations": []}`

Semantic result: PASS. This case is retained as a historical control. Its provenance check is part of the shared provenance-contract finding below.

### sim-v6-0057

`Médico: A dor voltou?
Paciente: Só do lado esquerdo agora.`

**Segments**

- `sim-v6-0057:segment-01` (clinician): A dor voltou?
- `sim-v6-0057:segment-02` (patient): Só do lado esquerdo agora.

- Local mentions: `[{"surface": "dor", "concept_id": "symptom.pain", "segment_id": "sim-v6-0057:segment-01"}]`
- Candidate attributes: `[{"field": "laterality", "value": "left", "source_segment_id": "sim-v6-0057:segment-02", "rule": "_last_laterality + continuity attachment"}]`
- Selected antecedent: `{"antecedent": "dor", "segment_id": "sim-v6-0057:segment-01", "status": "selected"}`
- Resolved attributes: `{"negated": false, "certainty": "confirmed", "temporality": "current", "experiencer": "patient", "laterality": "left", "dose": null, "dose_value": null, "dose_unit": null, "frequency": null, "route": null, "status": null}`
- Resolved/projected relations: `[]`
- Expected: `{"fields": {"negated": false, "certainty": "confirmed", "temporality": "current", "experiencer": "patient", "laterality": "left", "dose": null, "dose_value": null, "dose_unit": null, "frequency": null, "route": null, "status": "present"}, "relations": [{"relation_type": "HAS_LATERALITY", "target": "laterality", "value": "left"}]}`

**0057-F1 — `RELATION_NOT_GENERATED`**

laterality is attached to the resolved mention, but the continuity path does not create HAS_LATERALITY for a cross-segment attribute-only answer

Evidence:
- stored policy-aligned laterality is left
- stored projected relations are empty
- _apply_continuity assigns laterality at cross_segment_context.py:373-381
- _materialize_authoritative reads only candidate_result.provenance['projection']['relations'] at cross_segment_context.py:153-167

### sim-v6-0058

`Médico: Qual dose da metformina?
Paciente: Aumentei para 850 mg ontem.`

**Segments**

- `sim-v6-0058:segment-01` (clinician): Qual dose da metformina?
- `sim-v6-0058:segment-02` (patient): Aumentei para 850 mg ontem.

- Local mentions: `[{"surface": "metformina", "concept_id": "medication.metformin", "segment_id": "sim-v6-0058:segment-01"}]`
- Candidate attributes: `[{"field": "dose", "value": "850 mg", "source_segment_id": "sim-v6-0058:segment-02", "rule": "_last_dose + continuity attachment"}, {"field": "dose_value", "value": "850", "source_segment_id": "sim-v6-0058:segment-02", "rule": "_last_dose + continuity attachment"}, {"field": "dose_unit", "value": "mg", "source_segment_id": "sim-v6-0058:segment-02", "rule": "_last_dose + continuity attachment"}, {"field": "temporality", "value": "past", "source_segment_id": "sim-v6-0058:segment-02", "cue": "ontem"}]`
- Selected antecedent: `{"antecedent": "metformina", "segment_id": "sim-v6-0058:segment-01", "status": "selected"}`
- Resolved attributes: `{"negated": false, "certainty": "confirmed", "temporality": "past", "experiencer": "patient", "laterality": null, "dose": "850 mg", "dose_value": "850", "dose_unit": "mg", "frequency": null, "route": null, "status": "active"}`
- Resolved/projected relations: `[]`
- Expected: `{"fields": {"negated": false, "certainty": "confirmed", "temporality": "current", "experiencer": "patient", "laterality": null, "dose": "850 mg", "dose_value": "850", "dose_unit": "mg", "frequency": null, "route": null, "status": "active"}, "relations": [{"relation_type": "HAS_DOSE", "target": "dose", "value": "850 mg"}]}`

**0058-F1 — `RELATION_NOT_GENERATED`**

the question-answer dose attachment populates dose fields, but HAS_DOSE is generated only by the local projection or the two-dose transition path; this answer contains one new dose and therefore reaches projection with no relation

Evidence:
- stored policy-aligned dose fields are all correct
- stored projected relations are empty
- _apply_continuity assigns dose fields at cross_segment_context.py:383-393
- _augment_transition_relations returns when fewer than two dose values are available, so a single answer dose is not projected

**0058-F2 — `TEMPORAL_OWNERSHIP_FAILURE`**

the temporal cue ontem is assigned to the medication mention itself, although the approved semantics treat the dose-change event time separately from the current medication state

Evidence:
- stored expected temporality is current and actual temporality is past
- _PAST_CUE includes ontem at cross_segment_context.py:49-52
- following-text logic overwrites current with past at cross_segment_context.py:400-402
- dose and active status are otherwise resolved correctly

## Provenance audit

The persisted check is `0/3`. This is classified as `PROVENANCE_MATERIALIZATION_FAILURE` with a contributing `HARNESS_NORMALIZATION_MISMATCH`. The failure is independent of the missing relation findings: relation absence explains relation metrics, but does not by itself explain why the provenance contract fails for 0056 as well.

Evidence:
- run_holdout_v6.py:_provenance_ok requires source_text == case.text
- cross_segment_context.py:_local_result passes target.text to the local adapter
- context_safety.py returns source_text=query.text for that localized candidate
- AuthoritativeProjectionWriter preserves local_candidate.provenance before adding resolved metadata

The contract decision remains a HUMAN GATE: choose whether the authoritative result must carry full-conversation provenance or an explicit segment-scoped provenance field, then align the evaluator and materializer. No automatic repair is authorized from this report.

## Decision state

- Resolver freeze: `PRESERVED`
- V6 policy-aligned result: `PASS`
- Holdout result: `FAIL`
- Post-holdout repair: `NOT_AUTHORIZED`
- V7: `BLOCKED`
- Shadow Integration: `BLOCKED`
- Production: `BLOCKED`

The next decision is whether to authorize a general repair for relation materialization and event/state temporal ownership, with a new unseen validation set. The consumed cases must not be reused as holdouts.
