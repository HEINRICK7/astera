# V6 Independent Holdout Evaluation

Status: **FAIL — HUMAN GATE**  
Freeze: `v6-repair-v6-freeze-2026-08-15.json`  
Policy: `SEM-STATUS-001 v1.2`  
Holdout run count: **1**  
Rerun: **FORBIDDEN**

## Aggregate result

| Metric | RAW | Policy-aligned |
|---|---:|---:|
| mention exact | 0.3333 | 0.6667 |
| relation exact | 0.0000 | 0.0000 |
| cross-segment resolution | 0.3333 | 0.6667 |
| attribute ownership | 1.0000 | 1.0000 |
| provenance check | 0.0000 | 0.0000 |

Independent holdout: **FAIL**.

## Case findings

### `sim-v6-0056`

Family experiencer, temporality, negation, ownership and mention fields matched. No relation was expected. The case passed its semantic field checks.

### `sim-v6-0057`

Laterality `left` was resolved, but the projected relation `HAS_LATERALITY` was absent. The gold `status=present` is excluded from the policy-aligned gate as a v1.2 gold-review item; this does not excuse the missing relation.

Result: **FAIL — relation materialization**.

### `sim-v6-0058`

Medication, dose, dose value, dose unit and active status were resolved. The result had:

- `temporality`: expected `current`, actual `past`;
- missing projected relation `HAS_DOSE` for `850 mg`.

Result: **FAIL — temporality and relation materialization**.

## Decision

- resolver freeze remains in force;
- no repair was applied after the holdout;
- no holdout was rerun;
- V7: **BLOCKED**;
- Shadow Integration: **BLOCKED**;
- Production: **BLOCKED**.

The V6 policy-aligned pass demonstrates corpus alignment, but the independent holdouts exposed generalization gaps in cross-segment relation projection and transition temporality. Further work requires a new HUMAN GATE decision.

Machine-readable result: `context-validation-v6-holdout-0056-0058-2026-08-15.json`.
