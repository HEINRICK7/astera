# Semantic Policy Adjudication — Residual Type C

Status: **ADJUDICATED — POLICY v1.1**  
Milestone: `Semantic Policy Adjudication — Residual Type C`  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

This is the adjudication record for the residual queue. Carlos Henrique supplied the human decisions on 2026-08-15. No resolver, gold, or V6 corpus data was changed.

## Queue summary

| Decision cluster | Findings | Candidate policy | Status |
|---|---:|---|---|
| `D-TEMP-001` — temporality semantics | 13 | `SEM-TEMP-001` v1.1 | **10 Type B / 3 Type A** |
| `D-FREQ-001` — frequency/ownership semantics | 2 | `SEM-FREQ-001` | **2 Type A** |
| `D-REL-EXTRA-001` — relation admissibility | 4 | `SEM-REL-002` | **4 Type A** |

The 19 rows below are findings, not necessarily unique cases. `sim-v6-0017` and `sim-v6-0020` each contribute both a frequency finding and an extra-relation finding.

All 19 items were applied individually in [v6-residual-type-c-adjudication-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/v6-residual-type-c-adjudication-2026-08-15.json). The resulting global classification is `TYPE_A=124`, `TYPE_B=10`, `TYPE_C=0`.

## D-TEMP-001 — temporality semantics

| # | case_id | text / segments | surface | gold → resolved | Candidate policy | Reason for ambiguity |
|---:|---|---|---|---|---|---|
| 1 | v6-r-003-3 | Diz que não vomitou mas teve enjoo e uma azia forte depois do almoço. | enjoo | current → past | `SEM-TEMP-001` | Is “depois do almoço” event/onset time only, while the assertion remains current, or does the report describe a past episode? |
| 2 | v6-r-003-3 | Diz que não vomitou mas teve enjoo e uma azia forte depois do almoço. | azia | current → past | `SEM-TEMP-001` | Same event-time versus assertion-time boundary as item 1. |
| 3 | v6-r-008-3 | Não relata calafrio mas teve febre e dor no corpo depois do almoço. | febre | current → past | `SEM-TEMP-001` | “Depois do almoço” may locate onset/event without making the current clinical assertion historical. |
| 4 | v6-r-008-3 | Não relata calafrio mas teve febre e dor no corpo depois do almoço. | dor no corpo | current → past | `SEM-TEMP-001` | Same policy boundary as item 3. |
| 5 | v6-c-001-1 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. na consulta de hoje | tontura | current → past | `SEM-TEMP-001` + `SEM-NEG-001` | Does “não tive” describe a past absence, or should the negated symptom be current relative to the consultation? |
| 6 | v6-c-001-2 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. no retorno desta semana | tontura | current → past | `SEM-TEMP-001` + `SEM-NEG-001` | Same negated-assertion time boundary with a different discourse suffix. |
| 7 | v6-c-001-3 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. durante a revisão clínica | tontura | current → past | `SEM-TEMP-001` + `SEM-NEG-001` | Same negated-assertion time boundary with a different discourse suffix. |
| 8 | v6-c-002-1 | Médico: Sua mãe teve câncer e diabetes? / Paciente: Teve, de mama. na consulta de hoje | mãe | current → past | `SEM-TEMP-001` + `SEM-EXP-001` | Family-history event is linguistically past, but the gold target is the conversationally current family mention. |
| 9 | v6-c-002-2 | Médico: Sua mãe teve câncer e diabetes? / Paciente: Teve, de mama. no retorno desta semana | mãe | current → past | `SEM-TEMP-001` + `SEM-EXP-001` | Same family-history and answer-anchoring boundary. |
| 10 | v6-c-002-3 | Médico: Sua mãe teve câncer e diabetes? / Paciente: Teve, de mama. durante a revisão clínica | mãe | current → past | `SEM-TEMP-001` + `SEM-EXP-001` | Same family-history and answer-anchoring boundary. |
| 11 | sim-v6-0013 | A cirurgia foi há anos; atualmente sente peso na perna esquerda. | cirurgia | past → current | `SEM-TEMP-001` | “Foi há anos” explicitly marks the surgery as historical; this appears to test whether event time belongs to the target. |
| 12 | sim-v6-0025 | O pai conviveu com hipertensão, enquanto a paciente nega pressão alta. | hipertensão | past → current | `SEM-TEMP-001` + `SEM-EXP-001` | Family experiencer and historical state are separate from the patient’s current negated symptom. |
| 13 | sim-v6-0026 | A avó sofreu um AVC, mas o paciente não apresenta fraqueza hoje. | AVC | past → current | `SEM-TEMP-001` + `SEM-EXP-001` | Family event is explicitly past; policy must define whether target temporality follows the event or the current discourse. |

## D-FREQ-001 — frequency/ownership semantics

| # | case_id | text / segments | surface | differing field: gold → resolved | Candidate policy | Reason for ambiguity |
|---:|---|---|---|---|---|---|
| 14 | sim-v6-0017 | Tomava ibuprofeno 200 mg se dor e passou a usar 400 mg a cada oito horas. | ibuprofeno | frequency: `a cada oito horas` → `se dor` | `SEM-DOSE-001` or new `SEM-FREQ-*` | The current frequency appears to be the post-transition value; policy must define whether “se dor” is retained only as historical `CHANGED_FROM`. |
| 15 | sim-v6-0020 | A levotiroxina passou de 75 mcg em jejum para 88 mcg antes do café. | levotiroxina | frequency: `antes do café` → `em jejum` | `SEM-DOSE-001` or new `SEM-FREQ-*` | “Em jejum” and “antes do café” may be equivalent instructions rather than a semantic change; normalization/admissibility is undefined. |

## D-REL-EXTRA-001 — relation admissibility / extra relations

For these rows, gold relations are shown as `[]` while the resolved projection contains the listed relation. The question is whether the relation is inadmissible, or whether the gold schema is incomplete under the approved transition semantics.

| # | case_id | text / segments | surface | gold relations → resolved relation | Candidate policy | Reason for ambiguity |
|---:|---|---|---|---|---|---|
| 16 | sim-v6-0016 | A dose de sertralina era 50 mg antes de dormir e virou 75 mg pela manhã. | sertralina | `[]` → `HAS_DOSE(dose, 50 mg)` | `SEM-REL-001` + `SEM-DOSE-001` or new `SEM-REL-EXTRA-*` | Is an attribute relation to the historical value admissible alongside `CHANGED_FROM`, or must only transition relations be projected? |
| 17 | sim-v6-0016 | A dose de sertralina era 50 mg antes de dormir e virou 75 mg pela manhã. | sertralina | `[]` → `HAS_FREQUENCY(frequency, antes de dormir)` | `SEM-REL-001` + `SEM-DOSE-001` or new `SEM-REL-EXTRA-*` | Same admissibility question for the historical frequency relation. |
| 18 | sim-v6-0017 | Tomava ibuprofeno 200 mg se dor e passou a usar 400 mg a cada oito horas. | ibuprofeno | `[]` → `HAS_FREQUENCY(frequency, se dor)` | `SEM-REL-001` + `SEM-DOSE-001` or new `SEM-REL-EXTRA-*` | Historical PRN frequency may be represented by `CHANGED_FROM`, but its ordinary `HAS_FREQUENCY` relation may be an extra projection. |
| 19 | sim-v6-0020 | A levotiroxina passou de 75 mcg em jejum para 88 mcg antes do café. | levotiroxina | `[]` → `HAS_FREQUENCY(frequency, em jejum)` | `SEM-REL-001` + `SEM-DOSE-001` or new `SEM-REL-EXTRA-*` | “Em jejum” may be equivalent or historical; relation admissibility depends on the frequency policy decision. |

## Adjudication result

```text
D-TEMP-001       APPROVE  SEM-TEMP-001 v1.1  10 Type B, 3 Type A
D-FREQ-001       APPROVE  SEM-FREQ-001 v1.0  2 Type A
D-REL-EXTRA-001  APPROVE  SEM-REL-002  v1.0  4 Type A
```

The 10 Type B items are recorded in [V6_RESIDUAL_GOLD_REVIEW_QUEUE.md](V6_RESIDUAL_GOLD_REVIEW_QUEUE.md). They are review-only and do not authorize resolver behavior.

## Human adjudication format

For each cluster, record:

```text
D-TEMP-001 / D-FREQ-001 / D-REL-EXTRA-001
Decision: APPROVE / REJECT / AMBIGUOUS
Policy: SEM-...
Version: ...
Rationale: ...
Item exceptions: ...
```

## Gate state

```text
resolver_changes = 0
gold_changes = 0
V6 checksum = 1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10
holdouts = NOT_EXECUTED
Shadow = BLOCKED
Production = BLOCKED
Repair V4 = EXECUTED TYPE_A ONLY — FAIL / HUMAN GATE
```

Exit criterion for policy satisfied: `TYPE_C_POLICY_UNDEFINED = 0`. The authorized Type-A-only V4 execution failed its hard gate; see [V6_REPAIR_V4_POLICY_1_1_REPORT.md](V6_REPAIR_V4_POLICY_1_1_REPORT.md). The workflow is stopped at HUMAN GATE.
