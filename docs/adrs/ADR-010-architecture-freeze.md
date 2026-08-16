# ADR-010 — Architecture Freeze

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Flow |
| **Categoria** | Architecture Governance |
| **Escopo** | Kernel, Cognitive Model, Contracts, Events e Plugin boundaries |

## Contexto

O Astera concluiu a especificação da plataforma, a Cognitive Architecture e o
Cognitive Validation Lab. O risco principal da etapa seguinte é continuar
criando abstrações em vez de implementar e validar os módulos já definidos.

## Decisão

A arquitetura da plataforma está congelada na versão 1.0. A equipe entra na
fase **Construction** e deve implementar os contratos e limites já definidos no
Astera Flow.

Durante o freeze, Builders MUST NOT criar, sem decisão do Astera Flow:

- novas entidades ou conceitos cognitivos;
- novos domínios, ciclos, especialistas ou boundaries;
- novos RFCs ou ADRs para justificar implementação incremental;
- atalhos que acoplem plugins ao Kernel ou a providers específicos.

Builders MAY criar código, testes, adapters, fixtures e documentação de módulo
necessários para implementar um contrato existente.

## Exceção controlada

Se o Cognitive Validation Lab demonstrar uma limitação concreta do modelo
congelado, o trabalho afetado deve ser interrompido apenas nesse ponto e seguir:

```text
CQA Failure → RFC de mudança → Architecture Review → Reality Review
→ Medical Validation → ADR → Astera Flow → Implementação
```

Uma dúvida de implementação não é, por si só, uma mudança arquitetural. O
Builder deve resolver a dúvida usando os contratos existentes e registrar a
decisão no Journal do módulo.

## Consequências

- O Kernel e o Cognitive Model permanecem estáveis.
- Plugins podem evoluir independentemente dentro de suas boundaries.
- `pytest` valida software; o Cognitive Validation Lab valida o modelo de
  raciocínio. Os resultados permanecem separados.
- Cada sprint da Construction entrega código executável, testes, health check,
  observabilidade e validação de integração.

## Astera Flow

- Aba: `Construction`
- Versão: `1.0`
- Estado: `Approved`

## Referências

- [ADR-009 — Cognitive Architecture como especificação normativa](ADR-009-cognitive-architecture-specification.md)
- [Construction](../astera-flow/construction/README.md)
- [Cognitive Validation Lab](../astera-flow/cognitive-validation-lab/README.md)
