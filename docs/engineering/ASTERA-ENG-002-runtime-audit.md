---
document_id: astera-eng-002
title: Runtime Audit
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ASTERA-ENG-001-runtime-definition-of-done.md
  - ASTERA-ENG-003-runtime-integration-contract.md
used_by:
  - Product Engineering
  - Clinical Validation
last_updated: 2026-08-10
---

# ASTERA-ENG-002 — Runtime Audit

## Objetivo

Descobrir se o código novo percorre o Runtime real. A auditoria é somente
observacional e não altera código.

## Contexto

Uma feature pode existir, ter testes e ainda estar fora do caminho de execução.

## Arquitetura

O objeto auditado é a cadeia entre implementação, Runtime, interface e
consulta real.

## Fluxo

```text
Código → instanciação → chamada → evento → consumidor → consulta real
```

## Responsabilidades

Toda auditoria deve procurar:

- código morto;
- providers antigos;
- adapters não utilizados;
- eventos nunca emitidos;
- eventos nunca consumidos;
- projections mortas;
- reducers mortos;
- classes nunca instanciadas;
- métodos nunca chamados;
- duplicações e pipelines legados.

## Princípios

A auditoria não corrige, mascara ou reclassifica o comportamento encontrado.

## Critérios

Cada item recebe exatamente uma classificação:

```text
IMPLEMENTADO
EXECUTANDO
NÃO EXECUTANDO
```

“Implementado” sem evidência de execução não equivale a “Executando”.

## Objetivo final

Toda Sprint termina com um relatório de auditoria baseado em evidências.
