# D1 Prediction Boundary Audit

Status: **HUMAN GATE**

Audited only the persisted D1 traces. D1 was not rerun.

## Classification counts

- `TRACE_GRANULARITY_INSUFFICIENT`: `16`
- `EVALUATOR_CONTRACT_MISMATCH`: `0`
- `PREDICTION_FIELD_DEFAULTED`: `0`
- `PREDICTION_FIELD_DROPPED`: `0`
- `PREDICTION_FIELD_TRANSFORMED`: `0`
- `PREDICTION_MENTION_DROPPED`: `0`
- `PREDICTION_MENTION_EXTRA`: `0`
- `PREDICTION_RELATION_DROPPED`: `0`
- `SERIALIZATION_MISMATCH`: `0`

## Findings

- `D1-003` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-004` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-006` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-008` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-012` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-015` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-020` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-021` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-022` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-023` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-024` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-030` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-031` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-032` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-034` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`
- `D1-036` — `TRACE_GRANULARITY_INSUFFICIENT`; confidence `0.9`; repair class `INDETERMINATE`

All cases where `final_projection` equals `prediction` but both differ from gold are `TRACE_GRANULARITY_INSUFFICIENT`; the saved trace cannot prove a prediction mapping bug.
