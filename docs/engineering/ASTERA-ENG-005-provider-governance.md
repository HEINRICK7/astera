---
document_id: astera-eng-005
title: Provider Governance
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ASTERA-ENG-002-runtime-audit.md
  - ASTERA-ENG-006-end-to-end-validation.md
used_by:
  - Runtime Engineering
  - Platform Engineering
  - Release Engineering
last_updated: 2026-08-10
---

# ASTERA-ENG-005 — Provider Governance

## Objetivo

Tornar inequívoco qual provider está sendo utilizado em cada execução.

## Contexto

Código de múltiplos providers pode dar a falsa impressão de que todos estão
ativos.

## Arquitetura

Todo provider possui exatamente um estado:

```text
ACTIVE | INACTIVE | EXPERIMENTAL | DEPRECATED
```

## Responsabilidades

O Runtime deve registrar:

- capability;
- provider ativo;
- modelo e versão;
- ambiente;
- parâmetros relevantes;
- estado dos demais providers.

## Fluxo

Configuração → seleção → instanciação → chamada → telemetria do provider.

## Princípios

Provider disponível não significa provider ativo.

## Critérios

Uma consulta validada deve mostrar o provider efetivamente selecionado. Provider
presente no código, mas não selecionado, não pode ser reportado como ativo.

## Objetivo final

Não existir dúvida entre provider implementado, provider disponível e provider
executado.
