# V6 Residual Gold Review Queue

Status: **REVIEW-ONLY — NO AUTOMATIC GOLD CHANGE**  
Policy: `CLINICAL_SEMANTIC_POLICY` v1.1  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

These 10 findings were adjudicated as `TYPE_B_GOLD_ISSUE`. They must not drive resolver repair and must not be changed automatically in the frozen V6 corpus.

| # | case_id | Text / segments | Surface | Gold → resolved | Reason |
|---:|---|---|---|---|---|
| 1 | v6-r-003-3 | Diz que não vomitou mas teve enjoo e uma azia forte depois do almoço. | enjoo | current → past | Gold conflicts with event-time policy. |
| 2 | v6-r-003-3 | Diz que não vomitou mas teve enjoo e uma azia forte depois do almoço. | azia | current → past | Gold conflicts with event-time policy. |
| 3 | v6-r-008-3 | Não relata calafrio mas teve febre e dor no corpo depois do almoço. | febre | current → past | Gold conflicts with event-time policy. |
| 4 | v6-r-008-3 | Não relata calafrio mas teve febre e dor no corpo depois do almoço. | dor no corpo | current → past | Gold conflicts with event-time policy. |
| 5 | v6-c-001-1 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. na consulta de hoje | tontura | current → past | Past negated absence is represented as past under `SEM-TEMP-001`. |
| 6 | v6-c-001-2 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. no retorno desta semana | tontura | current → past | Past negated absence is represented as past under `SEM-TEMP-001`. |
| 7 | v6-c-001-3 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. durante a revisão clínica | tontura | current → past | Past negated absence is represented as past under `SEM-TEMP-001`. |
| 8 | v6-c-002-1 | Médico: Sua mãe teve câncer e diabetes? / Paciente: Teve, de mama. na consulta de hoje | mãe | current → past | Person/experiencer reference should have `temporality=null`; gold ownership is wrong. |
| 9 | v6-c-002-2 | Médico: Sua mãe teve câncer e diabetes? / Paciente: Teve, de mama. no retorno desta semana | mãe | current → past | Person/experiencer reference should have `temporality=null`; gold ownership is wrong. |
| 10 | v6-c-002-3 | Médico: Sua mãe teve câncer e diabetes? / Paciente: Teve, de mama. durante a revisão clínica | mãe | current → past | Person/experiencer reference should have `temporality=null`; gold ownership is wrong. |

## Required handling

- Preserve the V6 corpus and checksum.
- Do not train or repair the resolver to reproduce these gold values.
- Keep the 10 items available for a future human-approved corpus revision.
- Record the `mãe` items as a temporal ownership invariant: temporal attribution belongs to the clinical event, not automatically to the experiencer reference.

Machine-readable source: [v6-residual-type-c-adjudication-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/v6-residual-type-c-adjudication-2026-08-15.json).
