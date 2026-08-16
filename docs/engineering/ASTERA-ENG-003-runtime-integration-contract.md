---
document_id: astera-eng-003
title: Runtime Integration Contract
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ASTERA-ENG-001-runtime-definition-of-done.md
  - ASTERA-ENG-004-execution-trace.md
used_by:
  - Runtime Engineering
  - Workbench Engineering
  - Clinical Validation
last_updated: 2026-08-10
---

# ASTERA-ENG-003 — Runtime Integration Contract

## Objetivo

Provar a cadeia completa de uma feature desde a entrada até a interface.

## Contexto

Uma API ou classe isolada não comprova integração. Cada fronteira deve ser
observável no caminho real.

## Arquitetura

```text
Play → Audio → Speech Runtime → Clinical Runtime → Knowledge
  → Presentation → A2UI → React → Tela
```

## Responsabilidades

Para cada etapa, o registro deve informar:

- arquivo;
- classe ou função;
- método chamado;
- evento produzido;
- consumidor;
- evidência da consulta real.

## Fluxo

Cada etapa deve ser seguida até o próximo consumidor, sem salto implícito.

## Princípios

Contrato sem chamada observada não é integração.

## Critérios

Se uma etapa não tiver chamada observada e consumidor identificado, a feature é
`NÃO INTEGRADA`.

## Objetivo final

Toda capacidade deve ser rastreável do input original até o comportamento
visível na tela.
