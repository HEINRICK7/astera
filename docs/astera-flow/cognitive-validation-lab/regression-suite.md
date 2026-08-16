# Regression Suite de Capabilities

| Campo | Valor |
|---|---|
| **Status** | Active |
| **Responsável** | Cognitive Validator |

## Objetivo

Garantir que uma alteração em provider, plugin ou implementação não degrade
uma capability e seus casos cognitivos já certificados.

## Entrada

Uma capability entra na Regression Suite quando possui Validation Report, provenance,
critérios de comparação e verdict mínimo `pass_with_gaps` aprovado pelo Lab.

## Regressões monitoradas

- perda de Clinical Facts;
- mudança de versão ou ordem do Context;
- hipótese sem suporte ou gap desaparecido;
- Knowledge Query que deixa de ser justificável;
- aumento de informação inventada;
- SOAP/FHIR divergente do Context;
- lifecycle ou evento quebrado;
- mudança de owner entre Specialists.

## Regra de execução

```text
Alteração → CQA Regression Session → Comparação com baseline
          → Failure Analysis → decisão de promoção
```

O resultado da Regression Suite é independente de `pytest`. Um teste de
software pode passar enquanto a representação cognitiva regredi.
