# D1 Relation Boundary Audit

Status: **HUMAN GATE**

Audited only the persisted D1 traces. D1 was not rerun.

## Classification counts

- `RELATION_MISSING`: `9`
- `RELATION_EXTRA`: `7`
- `ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED`: `6`
- `RELATION_WRONG_TYPE`: `4`
- `RELATION_WRONG_VALUE`: `2`
- `RELATION_DUPLICATED`: `0`
- `RELATION_HISTORICAL_AS_CURRENT`: `0`
- `RELATION_WRONG_ENDPOINT`: `0`

## Findings

- `D1-002` mention `0` — `RELATION_EXTRA`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}`; count `1`; repair class `G1`
- `D1-005` mention `0` — `RELATION_MISSING`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'todas as noites'}`; count `1`; repair class `G1`
- `D1-010` mention `0` — `RELATION_MISSING`: `{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '25 mg'}`; count `1`; repair class `G1`
- `D1-010` mention `0` — `ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED`: `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '12,5 mg'}`; count `1`; repair class `G1`
- `D1-010` mention `0` — `RELATION_WRONG_TYPE`: `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '25 mg'}`; count `1`; repair class `G1`
- `D1-011` mention `0` — `ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED`: `{'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}`; count `1`; repair class `G1`
- `D1-013` mention `0` — `RELATION_MISSING`: `{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '300 mg'}`; count `1`; repair class `G1`
- `D1-013` mention `0` — `ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED`: `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '400 mg'}`; count `1`; repair class `G1`
- `D1-013` mention `0` — `RELATION_WRONG_TYPE`: `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '300 mg'}`; count `1`; repair class `G1`
- `D1-014` mention `0` — `ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED`: `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '7 mg'}`; count `1`; repair class `G1`
- `D1-014` mention `0` — `RELATION_WRONG_TYPE`: `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '14 mg'}`; count `1`; repair class `G1`
- `D1-016` mention `0` — `RELATION_MISSING`: `{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'duas vezes ao dia'}`; count `1`; repair class `G1`
- `D1-016` mention `0` — `ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'uma vez ao dia'}`; count `1`; repair class `G1`
- `D1-016` mention `0` — `RELATION_WRONG_TYPE`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'duas vezes ao dia'}`; count `1`; repair class `G1`
- `D1-017` mention `0` — `RELATION_MISSING`: `{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'pela manhã'}`; count `1`; repair class `G1`
- `D1-017` mention `0` — `ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}`; count `1`; repair class `G1`
- `D1-017` mention `0` — `RELATION_WRONG_VALUE`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'depois do jantar'}`; count `1`; repair class `G1`
- `D1-018` mention `0` — `RELATION_MISSING`: `{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'dias alternados'}`; count `1`; repair class `G1`
- `D1-018` mention `0` — `RELATION_MISSING`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'todos os dias'}`; count `1`; repair class `G1`
- `D1-019` mention `0` — `RELATION_EXTRA`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'pela manhã'}`; count `1`; repair class `G1`
- `D1-019` mention `1` — `RELATION_EXTRA`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'pela manhã'}`; count `1`; repair class `G1`
- `D1-025` mention `0` — `RELATION_EXTRA`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'depois do café'}`; count `1`; repair class `G1`
- `D1-025` mention `1` — `RELATION_EXTRA`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'depois do café'}`; count `1`; repair class `G1`
- `D1-027` mention `0` — `RELATION_EXTRA`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}`; count `1`; repair class `G1`
- `D1-027` mention `1` — `RELATION_EXTRA`: `{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'à noite'}`; count `1`; repair class `G1`
- `D1-028` mention `0` — `RELATION_MISSING`: `{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '40 mg'}`; count `1`; repair class `G1`
- `D1-033` mention `0` — `RELATION_WRONG_VALUE`: `{'relation_type': 'HAS_LATERALITY', 'target': 'laterality', 'value': 'right'}`; count `1`; repair class `G1`
- `D1-035` mention `0` — `RELATION_MISSING`: `{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'à noite'}`; count `1`; repair class `G1`

Interpretation: a missing derived relation with its attribute already present in `resolved_semantics` is a relation materialization G1. No reference or ownership failure is assigned without trace evidence.
