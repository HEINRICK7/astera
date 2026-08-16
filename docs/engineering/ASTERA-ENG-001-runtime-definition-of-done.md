---
document_id: astera-eng-001
title: Runtime Definition of Done
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ../AGENTS.md
  - ../DOCUMENT_CONVENTIONS.md
used_by:
  - Product Engineering
  - Release Engineering
last_updated: 2026-08-10
---

# ASTERA-ENG-001 — Runtime Definition of Done

## Objetivo

Definir quando uma feature pode ser considerada concluída.

## Contexto

Código compilando e testes unitários passando não provam que o Runtime utiliza
uma funcionalidade durante uma consulta.

## Arquitetura

Toda feature percorre exatamente estes estados:

```text
PLANNED → SPECIFIED → IMPLEMENTED → INTEGRATED → VALIDATED → RELEASED
```

## Responsabilidades

- `IMPLEMENTED`: o código existe.
- `INTEGRATED`: o Runtime instancia, chama e consome o código.
- `VALIDATED`: a execução foi observada em consulta real.
- `RELEASED`: o gate de release foi aprovado.

## Fluxo

Cada estado só avança quando a evidência do estado anterior estiver registrada.

## Princípios

Existência de código nunca substitui prova de execução.

## Critérios

Uma feature sem `VALIDATED` é `INCOMPLETE`, mesmo que compile ou tenha testes.
Cada transição deve possuir evidência rastreável: arquivos, chamadas, eventos,
logs, métricas e consulta real.

## Objetivo final

Nenhum trabalho pode ser reportado como concluído apenas por existência de
código.
