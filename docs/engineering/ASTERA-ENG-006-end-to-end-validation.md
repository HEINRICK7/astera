---
document_id: astera-eng-006
title: End-to-End Validation
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ASTERA-ENG-003-runtime-integration-contract.md
  - ASTERA-ENG-004-execution-trace.md
used_by:
  - Clinical Validation
  - Product Engineering
  - Release Engineering
last_updated: 2026-08-10
---

# ASTERA-ENG-006 — End-to-End Validation

## Objetivo

Validar o comportamento completo antes do encerramento de uma Sprint.

## Contexto

Mocks, doubles e pipelines sintéticos validam contratos, mas não provam que a
consulta real funciona.

## Arquitetura

A validação percorre o mesmo Runtime e a mesma interface usados pelo usuário.

## Fluxo

```text
Consulta → Speech → Transcript → Clinical Facts → Knowledge
  → Hypotheses → SOAP → FHIR → A2UI → React
```

## Responsabilidades

A validação deve usar:

- áudio real ou conversa real;
- provider selecionado para o ambiente;
- Runtime real;
- interface real;
- logs e métricas reais.

## Princípios

Uma validação sintética pode apoiar desenvolvimento, mas nunca aprova release.

## Critérios

Não usar pipeline sintético como evidência final. Cada etapa deve produzir um
resultado visível ou uma evidência de ausência/falha.

## Objetivo final

Uma Sprint só pode ser aprovada quando a capacidade completa aparece durante
uma consulta real.
