---
document_id: astera-eng-008
title: Architecture Drift
category: Engineering
status: Official
version: 1.0
owner: Astera Architecture
depends_on:
  - ASTERA-ENG-002-runtime-audit.md
  - ASTERA-ENG-003-runtime-integration-contract.md
used_by:
  - Architecture
  - Product Engineering
  - Release Engineering
last_updated: 2026-08-10
---

# ASTERA-ENG-008 — Architecture Drift

## Objetivo

Detectar automaticamente divergências entre decisão, código, Runtime e React.

## Contexto

Uma implementação pode seguir o ADR no nome e continuar usando o pipeline
antigo na execução.

## Arquitetura

O comparador confronta ADR, código, Runtime e React na ordem da execução.

## Fluxo

```text
ADR → Código → Runtime → React
```

## Responsabilidades

As verificações devem comparar:

- contratos e eventos declarados;
- providers selecionados;
- classes instanciadas;
- métodos chamados;
- consumidores ativos;
- estado exibido na interface;
- evidências do Execution Trace.

## Princípios

Divergência descoberta é falha de governança, não detalhe documental.

## Critérios

Qualquer divergência deve falhar a auditoria e impedir a classificação como
`VALIDATED`.

## Objetivo final

Impedir que documentação, código e execução evoluam como sistemas diferentes.
