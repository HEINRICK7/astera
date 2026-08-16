# ADR-009: Cognitive Architecture como especificação normativa

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team / Astera Flow |
| **Categoria** | Architecture Governance · Cognitive Architecture |
| **RFC** | RFC-001 |

## Contexto

Os cinco workshops da C.5 definiram conceitos importantes, mas ainda estavam
distribuídos entre notas, workshops e ADRs. Implementar diretamente a partir
dessas notas poderia gerar contratos incompletos e inconsistentes. Também é
necessário validar a arquitetura em um atendimento ponta a ponta antes da
Fase D.

## Decisão

Criar o domínio normativo `Cognitive Architecture` no Astera Flow, composto por
RFC-001, documentos 01–09, Workshop 6 de validação e o ciclo:

```text
Workshop → RFC → Architecture Review → Engineering Review
         → Reality Review → Medical Validation
         → ADR → Astera Flow → Implementação
```

O Astera Flow passa a ser a Design Authority para arquitetura cognitiva,
domínio clínico, comportamento dos Specialists e contratos de contexto.

## Papéis

- Cognitive Architect;
- Domain Reviewer;
- Medical Validator;
- Engineering Reviewer;
- Executor, somente após autorização.

## Consequências

- Especificação passa a preceder código.
- Os cinco workshops ganham contratos e critérios de validação comuns.
- O sexto workshop testa a evolução completa de um atendimento.
- Revisões ficam rastreáveis e separadas da execução.
- Código existente não é automaticamente reescrito por esta ADR.

## Limites

Esta ADR foi aprovada pelo Astera Flow e formaliza a especificação que orienta
a Construction. A ADR-010 congela a arquitetura e permite a implementação dos
contratos aprovados sem criar novas abstrações.

## Referências

- [RFC-001](../astera-flow/cognitive-architecture/RFC-001-astera-cognitive-architecture.md)
- [Cognitive Architecture](../astera-flow/cognitive-architecture/README.md)
- [ADR-003 — Workshops](ADR-003-cognitive-architecture-workshops.md)

## Próximas etapas normativas

- [Reality Review](../astera-flow/cognitive-architecture/12-reality-review.md)
- [Reality Case Registry](../astera-flow/cognitive-architecture/13-reality-case-registry.md)
- Medical Validation após evidência dos dez casos.
