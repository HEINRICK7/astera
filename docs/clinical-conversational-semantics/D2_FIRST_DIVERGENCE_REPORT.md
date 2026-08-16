# D2 First Divergence Report

Status: **HUMAN GATE**

D2 was executed once with Trace Granularity v2. This report is generated from the saved traces; the analyzer never invokes the resolver.

## Metrics

- `mention_exact_match`: `0.250000`
- `cross_segment_resolution`: `0.193548`
- `cross_mention_isolation`: `0.222222`
- `provenance`: `1.000000`
- `relation_exact_match`: `0.133333`
- `relation_materialization`: `0.235294`
- `relation_provenance`: `0.235294`

## D1 → D2 historical comparison

This is descriptive only; D1 was not rerun.

| Metric | D1 | D2 |
|---|---:|---:|
| mention exact | 0.139535 | 0.250000 |
| relation exact | 0.176471 | 0.133333 |
| cross-segment | 0.125000 | 0.193548 |
| cross-mention isolation | 0.138889 | 0.222222 |
| provenance | 1.000000 | 1.000000 |
| first divergence: generated_relations | 15 | 14 |
| first divergence: prediction | 16 | 14 |

The relation repair cannot be declared generalized from relation exact alone:
D2 relation exact is lower in this sample. The v2 traces do show the same
boundary is observable, with 14 relation-first cases and relation-level
materialization/provenance metrics recorded separately.

## First divergence stages

- `generated_relations`: `14`
- `prediction`: `14`

## Findings

- `D2-001` — `generated_relations` / `relations`: `[{'relation_type': 'HAS_LATERALITY', 'target': 'laterality', 'value': 'left'}]` → `[]`; confidence `0.86`; class `G1`
- `D2-002` — `prediction` / `status`: `None` → `discontinued`; confidence `0.55`; class `INDETERMINATE`
- `D2-004` — `generated_relations` / `relations`: `[]` → `[{'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}]`; confidence `0.86`; class `G1`
- `D2-006` — `prediction` / `experiencer`: `patient` → `family`; confidence `0.55`; class `INDETERMINATE`
- `D2-008` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `INDETERMINATE`
- `D2-010` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '50 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '25 mg'}]` → `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '50 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '50 mg'}]`; confidence `0.86`; class `G1`
- `D2-011` — `generated_relations` / `relations`: `[{'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}, {'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}]` → `[]`; confidence `0.86`; class `G1`
- `D2-012` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `INDETERMINATE`
- `D2-013` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '20 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '10 mg'}]` → `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '20 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '20 mg'}]`; confidence `0.86`; class `G1`
- `D2-014` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '50 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '75 mg'}]` → `[{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '75 mg'}]`; confidence `0.86`; class `G1`
- `D2-015` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '14 mg'}, {'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '7 mg'}]` → `[{'relation_type': 'CHANGED_FROM', 'target': 'dose', 'value': '14 mg'}]`; confidence `0.86`; class `G1`
- `D2-016` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'duas vezes ao dia'}, {'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'uma vez ao dia'}]` → `[{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'duas vezes ao dia'}]`; confidence `0.86`; class `G1`
- `D2-017` — `prediction` / `status`: `active` → `None`; confidence `0.55`; class `INDETERMINATE`
- `D2-018` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'todos os dias'}, {'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'dias alternados'}]` → `[]`; confidence `0.86`; class `G1`
- `D2-020` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `INDETERMINATE`
- `D2-023` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `INDETERMINATE`
- `D2-024` — `prediction` / `temporality`: `past` → `current`; confidence `0.55`; class `INDETERMINATE`
- `D2-025` — `prediction` / `frequency`: `None` → `após o almoço`; confidence `0.55`; class `INDETERMINATE`
- `D2-026` — `generated_relations` / `relations`: `[{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '5 mg'}]` → `[]`; confidence `0.86`; class `G1`
- `D2-027` — `prediction` / `frequency`: `None` → `à noite`; confidence `0.55`; class `INDETERMINATE`
- `D2-028` — `generated_relations` / `relations`: `[{'relation_type': 'HAS_DOSE', 'target': 'dose', 'value': '850 mg'}]` → `[]`; confidence `0.86`; class `G1`
- `D2-030` — `generated_relations` / `relations`: `[{'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}, {'relation_type': 'DISCONTINUED_AT', 'target': 'status', 'value': 'discontinued'}]` → `[]`; confidence `0.86`; class `G1`
- `D2-031` — `prediction` / `certainty`: `possible` → `confirmed`; confidence `0.55`; class `INDETERMINATE`
- `D2-032` — `prediction` / `temporality`: `past` → `current`; confidence `0.55`; class `INDETERMINATE`
- `D2-033` — `generated_relations` / `relations`: `[{'relation_type': 'HAS_LATERALITY', 'target': 'laterality', 'value': 'left'}]` → `[]`; confidence `0.86`; class `G1`
- `D2-034` — `prediction` / `negated`: `False` → `True`; confidence `0.55`; class `INDETERMINATE`
- `D2-035` — `generated_relations` / `relations`: `[{'relation_type': 'CHANGED_FROM', 'target': 'frequency', 'value': 'à noite'}, {'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'pela manhã'}]` → `[{'relation_type': 'HAS_FREQUENCY', 'target': 'frequency', 'value': 'pela manhã'}]`; confidence `0.86`; class `G1`
- `D2-036` — `prediction` / `certainty`: `possible` → `confirmed`; confidence `0.55`; class `INDETERMINATE`

D1 was not rerun. D2 is diagnostic evidence only; no repair is authorized by this result.

## Execution integrity note

Two precondition-aborted attempts exposed gold occurrence errors before the
official run completed. Their partial traces are quarantined under
`d2-invalid-attempt-*` and are excluded from every D2 metric. The official
one-shot consists only of execution
`d2-one-shot-4368c4a3-530d-4ffc-bb41-610928825409`, with 36/36 valid v2 traces.
