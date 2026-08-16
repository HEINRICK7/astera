---
document_id: astera-eng-009
title: Source of Truth
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ASTERA-ENG-004-execution-trace.md
  - ASTERA-ENG-006-end-to-end-validation.md
used_by:
  - All Engineering Teams
  - Clinical Validation
last_updated: 2026-08-10
---

# ASTERA-ENG-009 — Source of Truth

## Objetivo

Definir qual evidência representa a verdade operacional do Astera.

## Contexto

Código, testes e documentação descrevem intenção ou possibilidade. Nenhum deles
prova sozinho o comportamento em produção ou desenvolvimento integrado.

## Fluxo

Consulta real → Runtime observado → estado projetado na interface.

## Princípios

Intenção arquitetural não substitui comportamento verificável.

## Arquitetura

```text
Consulta Real → Runtime → Interface
```

## Responsabilidades

Código, testes e documentos devem refletir a execução observada. Quando houver
conflito, a divergência deve ser registrada e a feature permanece incompleta.

## Critérios

Não considerar como verdade única:

- classe existente;
- teste passando;
- documentação dizendo “implementado”;
- snapshot sem trace da sessão viva.

## Objetivo final

O estado aceito do produto é o estado comprovado durante a consulta real e
refletido pela interface.
