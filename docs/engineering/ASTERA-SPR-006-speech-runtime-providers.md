---
document_id: astera-spr-006
title: XAI Speech Provider Migration
category: Engineering Sprint
status: IMPLEMENTED — GOLDEN AUDIO VALIDATION PENDING
priority: CRITICAL
last_updated: 2026-08-10
---

# ASTERA-SPR-006 — XAI Speech Provider Migration

## Resultado

O provider ativo de Speech passou a ser o streaming Speech-to-Text da xAI.
Faster Whisper permanece disponível somente como provider legado de
desenvolvimento e testes.

```text
Workbench / Desktop
  ↓ PCM 16 kHz
Speech WebSocket
  ↓
SpeechEnginePort
  ↓
XAIStreamingSpeechProvider
  ↓
partial / revision / final
  ↓
StreamingTranscriptState
  ↓
Clinical Normalization Layer
  ↓
Clinical Runtime
  ↓
Knowledge Runtime
  ↓
Presentation Runtime
  ↓
A2UI
  ↓
RuntimeSessionProjection
  ↓
React
```

Clinical, Knowledge, Presentation, A2UI, RuntimeSessionProjection, React e UX
não foram alterados.

## Provider

O adapter usa exclusivamente o endpoint de Speech-to-Text streaming da xAI:

```text
wss://api.x.ai/v1/stt
```

Ele envia PCM como frames binários e configura `interim_results`,
`endpointing`, `diarize`, `vad_threshold` e termos clínicos de apoio. O
protocolo externo é convertido para `SpeechEvent` e, depois, para
`TranscriptSegment` provider-neutral.

O Voice Agent / Speech-to-Speech não é usado: o Astera precisa somente de
transcrição para alimentar seu próprio pipeline clínico.

## Eventos normalizados

O adapter converte:

```text
transcript.created → speech.started
transcript.partial (is_final=false) → speech.partial
transcript.partial (revisão) → speech.revision
transcript.partial (is_final=true) → speech.final
transcript.done → encerramento do stream
error → speech.error
```

O `SpeechEnginePort` continua sendo a única fronteira conhecida pelo
`LiveClinicalPipeline`. Providers futuros, como Parakeet, OpenAI, Azure ou
AWS, devem implementar o mesmo contrato.

## Configuração

```text
ASTERA_SPEECH_PROVIDER=streaming
ASTERA_XAI_API_KEY=<secret>
ASTERA_XAI_BASE_URL=https://api.x.ai/v1
```

O provider pode ser trocado sem alterar o pipeline:

```text
streaming       ACTIVE (xAI)
xai             ACTIVE alias
faster-whisper  LEGACY
parakeet        PLANNED
```

## Testes automatizados

- Adapter XAI com WebSocket fake e eventos partial/final.
- Conversão para `SpeechEvent` e `SpeechEnginePort`.
- Pipeline clínico existente preservado.
- Suíte completa: **132 passed**, 4 warnings de depreciação externa.

## Pendência de produto

O contrato e o adapter estão implementados, mas a Sprint só será `READY`
depois do Golden Audio real comprovar:

```text
XAI Speech
  → Clinical Mentions
  → Clinical Facts
  → Knowledge
  → Presentation
  → A2UI
  → RuntimeSessionProjection
  → React
```

Também devem ser registrados primeiro partial, final, revisão, latência,
Facts, Knowledge Objects, Presentation Objects, eventos A2UI e atualizações da
RuntimeSession.
