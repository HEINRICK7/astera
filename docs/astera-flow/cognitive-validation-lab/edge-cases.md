# Edge Cases

| Campo | Valor |
|---|---|
| **Status** | Proposed |
| **Responsável** | Cognitive Validator |

## Objetivo

Manter casos que tentam quebrar o modelo cognitivo, além da amostra regular de
dez consultas.

## Catálogo inicial

- paciente muda de assunto no meio da consulta;
- duas hipóteses entram em conflito;
- exame contradiz relato do paciente;
- médico discorda da hipótese ou Recommendation;
- guideline muda entre duas consultas;
- paciente nega algo que havia relatado antes;
- informação é fornecida por familiar, intérprete ou cuidador;
- consulta tem múltiplos problemas simultâneos;
- dado visual ou exame não cabe em texto;
- pergunta de alto valor muda a prioridade do atendimento;
- consulta termina antes de resolver Information Gaps;
- representação precisa indicar informação ausente sem inventar conteúdo.

## Critério

Cada edge case deve gerar um Validation Report e, se falhar, uma Failure
Analysis. Edge case não é motivo para inventar um conceito durante a sessão.
