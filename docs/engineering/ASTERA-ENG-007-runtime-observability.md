---
document_id: astera-eng-007
title: Runtime Observability
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ASTERA-ENG-004-execution-trace.md
  - ASTERA-ENG-005-provider-governance.md
used_by:
  - Runtime Engineering
  - Clinical Validation
  - Operations
last_updated: 2026-08-10
---

# ASTERA-ENG-007 — Runtime Observability

## Objetivo

Tornar visível o tempo e o estado de cada camada.

## Contexto

Contadores agregados podem esconder que uma etapa nunca aconteceu.

## Arquitetura

```text
Speech: first audio → first partial → first final
Clinical: first fact → first hypothesis → first SOAP
Presentation: first card → first patch → first timeline
React: first render → last update
```

## Responsabilidades

As métricas devem ser correlacionadas por consulta, sessão, provider e versão.
Ausência de um marco deve ser registrada como ausência, não como sucesso.

## Fluxo

Evento → timestamp → métrica → correlação → visualização → trace.

## Princípios

Zero, nulo, não emitido e não consumido são estados diferentes.

## Critérios

O painel e o trace devem distinguir `null`, zero, não emitido e não consumido.

## Objetivo final

Ser possível responder, com números, onde a experiência parou ou atrasou.
