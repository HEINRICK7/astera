# D3 ClinicalRelationCompiler Input Contract Audit

Status: **HUMAN GATE**

This audit reads only the 36 frozen D3 traces. D3 was not rerun and no compiler or resolver code was changed.

## Summary

- generated_relations first-divergence cases: `27`
- relation findings audited: `37`
- compiler bugs (`INPUT_CORRECT_COMPILER_WRONG`): `0`
- upstream input bugs: `36`
- incomplete inputs: `21`
- ambiguous inputs: `1`
- next decision: `C2`

## Interpretation

`INPUT_CORRECT_COMPILER_WRONG` requires typed owner identity, compatible ownership, correct current/transition state, supported endpoints and provenance before the compiler boundary. Missing or contradictory fields are not attributed to the compiler merely because the first evaluated mismatch is `generated_relations`.

## Relation matrices

### CHANGED_FROM

- findings: `5`
- `INPUT_WRONG_TRANSITION`: `5`

### DISCONTINUED_AT

- findings: `1`
- `INPUT_AMBIGUOUS`: `1`

### HAS_DOSE

- findings: `14`
- `INPUT_INCOMPLETE`: `9`
- `INPUT_WRONG_OWNER`: `1`
- `INPUT_WRONG_STATE`: `4`

### HAS_FREQUENCY

- findings: `13`
- `INPUT_INCOMPLETE`: `8`
- `INPUT_WRONG_OWNER`: `1`
- `INPUT_WRONG_STATE`: `4`

### HAS_LATERALITY

- findings: `4`
- `INPUT_INCOMPLETE`: `4`

## Findings

- `D3-001` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '6.25 mg'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-002` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '37.5 mg'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-003` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '100 mg'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-004` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '2.5 ml'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-005` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '25 mg'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-006` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '5 mg'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-007` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'ao acordar'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-008` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'de oito em oito horas'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-009` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'antes de dormir'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-010` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'depois do jantar'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-011` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'aos domingos'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-012` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'de 12 em 12 horas'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-013` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_LATERALITY', 'target': 'laterality', 'value': 'left'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-014` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_LATERALITY', 'target': 'laterality', 'value': 'right'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-019` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '15 mg'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-020` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'duas vezes ao dia'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-021` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '14 mg'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-022` m0 — `INPUT_WRONG_TRANSITION` — expected `{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'de manhã'}`; produced `None`; first incorrect field `transition_signal`; confidence `0.96`
- `D3-022` m0 — `INPUT_WRONG_STATE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}`; produced `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'de manhã'}`; first incorrect field `frequency`; confidence `0.96`
- `D3-022` m0 — `INPUT_WRONG_STATE` — expected `None`; produced `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'de manhã'}`; first incorrect field `frequency`; confidence `0.96`
- `D3-023` m0 — `INPUT_WRONG_TRANSITION` — expected `{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '40 mg'}`; produced `None`; first incorrect field `transition_signal`; confidence `0.96`
- `D3-023` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '20 mg'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-024` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'pela manhã'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-026` m0 — `INPUT_WRONG_TRANSITION` — expected `{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '50 mg'}`; produced `None`; first incorrect field `transition_signal`; confidence `0.96`
- `D3-026` m0 — `INPUT_WRONG_STATE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '75 mg'}`; produced `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '50 mg'}`; first incorrect field `dose`; confidence `0.96`
- `D3-026` m0 — `INPUT_WRONG_STATE` — expected `None`; produced `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '50 mg'}`; first incorrect field `dose`; confidence `0.96`
- `D3-029` m0 — `INPUT_AMBIGUOUS` — expected `{'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}`; produced `None`; first incorrect field `gold_relation_contract`; confidence `0.99`
- `D3-031` m0 — `INPUT_WRONG_STATE` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'pela manhã'}`; produced `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}`; first incorrect field `frequency`; confidence `0.96`
- `D3-031` m0 — `INPUT_WRONG_STATE` — expected `None`; produced `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}`; first incorrect field `frequency`; confidence `0.96`
- `D3-032` m0 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_LATERALITY', 'target': 'laterality', 'value': 'right'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-032` m1 — `INPUT_INCOMPLETE` — expected `{'relation_type': 'HAS_LATERALITY', 'target': 'laterality', 'value': 'left'}`; produced `None`; first incorrect field `owner_signal`; confidence `0.96`
- `D3-033` m0 — `INPUT_WRONG_TRANSITION` — expected `None`; produced `{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '500 mg'}`; first incorrect field `transition_signal.value`; confidence `0.96`
- `D3-033` m1 — `INPUT_WRONG_TRANSITION` — expected `None`; produced `{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '500 mg'}`; first incorrect field `transition_signal.value`; confidence `0.96`
- `D3-035` m0 — `INPUT_WRONG_STATE` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '25 mg'}`; produced `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '50 mg'}`; first incorrect field `dose`; confidence `0.96`
- `D3-035` m0 — `INPUT_WRONG_STATE` — expected `None`; produced `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '50 mg'}`; first incorrect field `dose`; confidence `0.96`
- `D3-036` m1 — `INPUT_WRONG_OWNER` — expected `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '75 mg'}`; produced `None`; first incorrect field `owner_type`; confidence `0.96`
- `D3-036` m1 — `INPUT_WRONG_OWNER` — expected `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}`; produced `None`; first incorrect field `owner_type`; confidence `0.96`

No repair is authorized. D1, D2, V7 and D3 remain immutable historical evidence.
