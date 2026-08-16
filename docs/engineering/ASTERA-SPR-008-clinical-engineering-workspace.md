---
document_id: astera-spr-008
title: Clinical Engineering Workspace
category: Engineering Sprint
status: IMPLEMENTED — RUNTIME SMOKE PENDING
priority: HIGH
last_updated: 2026-08-10
---

# ASTERA-SPR-008 — Clinical Engineering Workspace

## Resultado

O Workbench passou a apresentar a `RuntimeSessionProjection` como uma tela
de engenharia em tempo real. A tela não possui estado clínico próprio, não
normaliza texto e não reconstrói Facts, Knowledge ou A2UI.

```text
Speech Runtime
  ↓
StreamingTranscriptState
  ↓
Clinical Mentions
  ↓
Clinical Facts
  ↓
Knowledge
  ↓
Presentation Objects
  ↓
A2UI Stream
  ↓
RuntimeSessionProjection
  ↓
React Renderer
```

## Superfícies

- Operational state dos runtimes.
- Speech Session e telemetria.
- Transcript completo, partials, finais e revisões.
- Clinical Mentions emitidas pelo Runtime.
- Clinical Facts com proveniência, confiança, polaridade e revisão.
- Knowledge Objects.
- Presentation Objects.
- A2UI stream e objetos ativos.
- Timeline completa de eventos.
- Health da RuntimeSessionProjection.

Não há nome, idade, sexo, convênio ou prontuário na tela.

## Contrato

O Runtime passou a publicar `clinical.mention.detected` com o objeto
provider-neutral da `ClinicalNormalizationLayer`. O Workbench apenas acumula
esse evento dentro de `RuntimeSessionProjection.clinicalMentions` e o
renderiza.

O fluxo continua compatível com a fonte única de verdade:

```text
RuntimeSessionProjection → React → renderer
```

## Validação

- Workbench: `npm run build` passou.
- Runtime: `132 passed`, 4 warnings de depreciação externa.
- Runtime reiniciado em `127.0.0.1:8011`.
- `/health`: `{"status":"alive"}`.
- Golden Audio funcional: pendente.
