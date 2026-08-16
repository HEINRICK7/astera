---
document_id: astera-spr-005
title: Clinical Normalization Layer
category: Engineering Sprint
status: IMPLEMENTED — GOLDEN AUDIO PENDING
priority: CRITICAL
last_updated: 2026-08-10
---

# ASTERA-SPR-005 — Clinical Normalization Layer

## Resultado

O caminho ativo do Runtime agora separa a transcrição da interpretação clínica:

```text
Audio
  ↓
Speech Runtime
  ↓
StreamingTranscriptState
  ↓
ConversationMemory
  ↓
Clinical Normalization Layer
  ↓
Clinical NLP / Clinical Facts
  ↓
Knowledge
  ↓
Presentation
  ↓
A2UI
  ↓
RuntimeSessionProjection
  ↓
React
```

`KeywordClinicalNlp` permanece somente como detector rápido auxiliar. Ele não é
mais a condição para o pipeline clínico continuar e não cria Facts diretamente.

## Contrato da camada

Para cada menção identificada, a camada produz `ClinicalMention` contendo:

- texto original e texto normalizado;
- `concept_id` e tipo semântico;
- confiança, negação e temporalidade;
- speaker, segmento, revisão e timestamp;
- proveniência e indicação de revisão manual.

O extractor existente converte essas menções em `ClinicalFact` preservando a
proveniência. Nenhuma mudança foi feita em RuntimeSession, Presentation, A2UI,
React ou na UX.

## Vocabulário inicial

A normalização determinística cobre, entre outras, as equivalências:

| Entrada | Conceito |
| --- | --- |
| pressão alta, hipertenso, HAS | Hipertensão |
| dor no peito, dor torácica | Dor torácica |
| vomitando sangue, hematemese, ematemese | Hematêmese |
| falta de ar, dispneia | Dispneia |
| losartana | Losartana |
| DM | Diabetes Mellitus |
| HDA | Hemorragia Digestiva Alta |

Negação, temporalidade passada, variantes fonéticas e candidatos vindos do
detector rápido são preservados como metadados de confiança e revisão.

## Observabilidade

O `speech.runtime.metrics` do mesmo Runtime passa a registrar:

`mentions_detected`, `mentions_normalized`, `mentions_negated`,
`mentions_review_required`, `normalization_latency_ms` e
`normalization_errors`.

## Validação automatizada

- Testes unitários para sinônimos, abreviações, variantes fonéticas, negação,
  temporalidade, speaker e proveniência.
- Teste de integração da fronteira `ClinicalMention → ClinicalFact`.
- Teste do pipeline fragmentado com contexto acumulado.
- Suíte completa: **129 passed**, 4 warnings de depreciação externa.

## Pendência de produto

O código e os contratos estão implementados e validados automaticamente. Ainda
falta executar o Golden Audio clínico no Runtime reiniciado e confirmar a cadeia
com fatos clínicos e cards A2UI no Workbench. Portanto, o SPR-005 não deve ser
marcado como concluído funcionalmente antes desse teste.
