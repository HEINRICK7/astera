# Post-V5 Mention State & Isolation Audit

Status: **DIAGNOSTIC ONLY — no repair authorized**  
Data: 2026-08-15  
Policy: `clinical-semantic-policy-v1.1`  
V6 checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

## Escopo e invariantes

A auditoria reconstrói o caminho policy-aligned do Repair V5 por menção.
Os 10 campos Type B são ignorados somente na comparação do campo
adjudicado; casos inteiros não são removidos. Resolver, corpus, policy,
gold, relações, provenance e arquitetura cross-segment não foram alterados.

## Decomposição de mention_exact_match

- mentions_total: **334**
- mentions_exact: **243**
- mentions_failed: **91**
- mentions_failed_only_status: **89**
- mentions_failed_only_temporality: **1**
- mentions_failed_only_negation: **0**
- mentions_failed_only_laterality: **0**
- mentions_failed_multiple_fields: **1**

| Failure reason | Count |
|---|---:|
| only_status | 89 |
| only_temporality | 1 |
| only_negation | 0 |
| only_laterality | 0 |
| multiple_fields | 1 |

## Status

- status_false_positive: **81**
- status_false_negative: **9**
- status_wrong_value: **0**

| Entity type | Mentions | Expected values | Actual values | Status mismatches |
|---|---:|---|---|---:|
| condition | 41 | {'None': 41} | {'None': 41} | 0 |
| device | 3 | {'active': 3} | {'active': 3} | 0 |
| event | 11 | {'None': 10, 'historical': 1} | {'historical': 11} | 10 |
| medication | 34 | {'active': 29, 'discontinued': 5} | {'active': 29, 'discontinued': 5} | 0 |
| person | 3 | {'None': 3} | {'historical': 3} | 3 |
| procedure | 1 | {'None': 1} | {'historical': 1} | 1 |
| symptom | 238 | {'None': 199, 'present': 37, 'historical': 1, 'resolved': 1} | {'present': 91, 'None': 141, 'historical': 5, 'resolved': 1} | 76 |
| time | 3 | {'None': 3} | {'None': 3} | 0 |

## Cross-mention leakage

- cross_mention_attribute_leak: **4**
- cross_mention_status_leak: **2**
- cross_mention_negation_leak: **1**
- cross_mention_temporality_leak: **1**
- cross_mention_laterality_leak: **0**

A definição operacional está no JSON de leakage. Ela é conservadora:
marca apenas valor de sibling gold ou provenance de segmento fora do
owner esperado.

## Métricas de controle

- relation_exact: **86/86**
- cross_segment_exact: **107/124**
- relations: **FROZEN**
- provenance: **FROZEN**
- cross-segment architecture: **FROZEN**

## Decisão

Este é um relatório diagnóstico. Não iniciar Repair V6, não alterar gold
ou policy e não executar holdouts, V7, Shadow Integration ou Production.
