---
document_id: astera-eng-011
title: Engineering Workflow
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ASTERA-ENG-001-runtime-definition-of-done.md
  - ASTERA-ENG-002-runtime-audit.md
  - ASTERA-ENG-003-runtime-integration-contract.md
  - ASTERA-ENG-004-execution-trace.md
  - ASTERA-ENG-006-end-to-end-validation.md
  - ASTERA-ENG-010-release-gate.md
used_by:
  - All Engineering Teams
  - Sprint Owners
last_updated: 2026-08-10
---

# ASTERA-ENG-011 — Engineering Workflow

## Objetivo

Tornar obrigatório o fluxo que leva uma decisão arquitetural até uma capacidade
comprovada na interface.

## Contexto

Sem uma ordem única, uma equipe pode parar em implementação ou teste unitário
sem integrar a feature ao Runtime.

## Arquitetura

```text
ADR
  ↓
Arquitetura
  ↓
Implementação
  ↓
Testes Unitários
  ↓
Testes de Integração
  ↓
Runtime Audit
  ↓
Execution Trace
  ↓
Consulta Real
  ↓
Validação Visual
  ↓
Release
```

## Responsabilidades

Cada etapa deve produzir uma evidência e alimentar a etapa seguinte. O Agent
deve registrar onde a alteração nasce, quem a instancia, quem a chama, quem a
consome e em qual consulta real executou.

## Fluxo

O trabalho só avança quando a evidência da etapa atual está disponível.

## Princípios

O Runtime é a fonte operacional da verdade e a interface é sua projeção.

## Critérios

Não é permitido pular `Runtime Audit`, `Execution Trace`, `Consulta Real` ou
`Validação Visual`. Falha em qualquer etapa bloqueia o release.

## Princípios permanentes

1. Código compilando não significa feature pronta.
2. Teste unitário não substitui Runtime.
3. Código existente não significa código executado.
4. Nenhum ADR é concluído sem consulta real.
5. Toda feature possui Execution Trace.
6. Toda Sprint termina com Runtime Audit.
7. Não desenvolver sobre código ainda não integrado.
8. Runtime é a fonte operacional da verdade; React apenas projeta.
9. Estado vivo tem precedência sobre snapshot quando disponível.
10. Toda alteração responde às perguntas de origem, instanciação, chamada,
    consumo e evidência.

## Objetivo final

Uma entrega só é aceita quando percorre toda a cadeia do ADR até a interface em
uma execução real.
