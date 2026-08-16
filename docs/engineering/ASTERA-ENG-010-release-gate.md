---
document_id: astera-eng-010
title: Release Gate
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ASTERA-ENG-001-runtime-definition-of-done.md
  - ASTERA-ENG-002-runtime-audit.md
  - ASTERA-ENG-006-end-to-end-validation.md
used_by:
  - Sprint Owners
  - Release Engineering
  - Architecture
last_updated: 2026-08-10
---

# ASTERA-ENG-010 — Release Gate

## Objetivo

Impedir o encerramento de uma Sprint sem evidência operacional suficiente.

## Contexto

“Pronto” precisa significar executado, observado e rastreado.

## Arquitetura

O gate consolida as evidências produzidas pela auditoria, pelo trace e pela
validação end-to-end.

## Fluxo

```text
Implementação → Audit → Trace → Consulta Real → Validação → Gate
```

## Responsabilidades

O responsável deve responder:

- Runtime usa o código novo?
- Eventos são publicados?
- React consome os eventos?
- Consulta foi validada?
- Logs confirmam?
- Métricas confirmam?
- Pipeline antigo foi removido ou explicitamente classificado?
- Código morto foi identificado?
- Provider ativo está documentado?

## Princípios

Respostas sem evidência devem ser tratadas como falhas do gate.

## Critérios

O resultado do gate é exatamente um:

```text
APROVADO | BLOQUEADO
```

Qualquer resposta sem evidência bloqueia o release.

## Objetivo final

Nenhuma Sprint é encerrada por compilação, intenção ou teste isolado.
