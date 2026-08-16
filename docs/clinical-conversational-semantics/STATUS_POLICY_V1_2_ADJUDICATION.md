# Clinical Status Semantics Adjudication — Policy v1.2

Status: **HUMAN GATE — POLICY v1.2 NOT APPROVED**  
Policy under review: `clinical-semantic-policy-v1.1 (under review; v1.2 not approved)`  
Frozen V6 checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

## Escopo

Esta fila usa somente divergências de `status` do audit pós-V5. Não altera resolver, gold, corpus, policy ou métricas. Os 89 casos `only_status` são falhas de menção exclusivamente por status; há 90 findings de campo porque um caso também diverge em negação.

## Contagens

- status mismatch findings: **90**
- status-only failures: **89**
- status plus another field: **1**

| Classification | Count |
|---|---:|
| EXPLICIT_LIFECYCLE_STATUS | 0 |
| IMPLICIT_ASSERTION_ONLY | 9 |
| TEMPORALITY_ONLY | 7 |
| NEGATION_ONLY | 0 |
| MEDICATION_LIFECYCLE | 0 |
| PROCEDURE_LIFECYCLE | 1 |
| EVENT_LIFECYCLE | 10 |
| NO_STATUS_EVIDENCE | 63 |

## Matriz por entidade

| Entity type | Classification | Count |
|---|---|---:|
| event | EVENT_LIFECYCLE | 10 |
| person | TEMPORALITY_ONLY | 3 |
| procedure | PROCEDURE_LIFECYCLE | 1 |
| symptom | IMPLICIT_ASSERTION_ONLY | 9 |
| symptom | NO_STATUS_EVIDENCE | 63 |
| symptom | TEMPORALITY_ONLY | 4 |

## Transições observadas

| Gold → resolved | Count |
|---|---:|
| None → historical | 18 |
| None → present | 63 |
| present → None | 9 |

## Hipótese normativa candidata (não aplicada)

- symptom/condition/person/event/procedure: `status=null` por default;
  lifecycle explícito exigiria decisão normativa própria;
- medication/device: preservar somente lifecycle explícito (`active`,
  `discontinued` ou vocabulário aprovado);
- passado de evento não deve transferir automaticamente `historical` para
  a menção nem para o experiencer; pode ser apenas `temporality=past`.

Essa é uma hipótese para adjudicação, não uma nova versão da policy.

## Decisões humanas necessárias

- whether positive assertion alone produces status=present
- whether historical event/procedure/person cues produce status or only temporality
- whether symptom lifecycle values such as ongoing/resolved are approved
- whether resolved may coexist with negated=true

## Fila completa

Os 90 findings, com texto, cues, valores e classificação, estão no JSON
`STATUS_EXPLICIT_CUE_ANALYSIS.json`.

## Invariantes

- resolver_changes = 0
- gold_changes = 0
- corpus_changes = 0
- policy_changes = 0
- repair_started = false
- relations, provenance e cross-segment architecture permanecem frozen
- holdouts, V7, Shadow e Production permanecem bloqueados
