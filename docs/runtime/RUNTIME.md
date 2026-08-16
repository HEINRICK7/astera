---
document_id: astera-runtime
title: Astera Runtime
category: Runtime
status: BASELINE — READY FOR PRODUCT VALIDATION
version: 2.0
owner: Astera Engineering
depends_on:
  - ../adrs/ADR-015-engineering-governance.md
  - ../engineering/ASTERA-ENG-003-runtime-integration-contract.md
  - ../engineering/ASTERA-ENG-008-architecture-drift.md
  - ../engineering/ASTERA-SPR-002-runtime-stabilization.md
  - ../engineering/ASTERA-SPR-006-speech-runtime-providers.md
used_by:
  - Runtime Engineering
  - Astera Workbench
last_updated: 2026-08-10
---

# Astera Runtime

## Pipeline de execução

O Runtime do Astera tem uma única cadeia de execução clínica:

```text
Player
  ↓
Speech WebSocket
  ↓
SpeechEnginePort
  ↓
StreamingTranscriptSession
  ↓
StreamingTranscriptState
  ↓
Clinical Runtime
  ↓
Knowledge Runtime
  ↓
Presentation Runtime
  ↓
A2UI Runtime
  ↓
Runtime Session
  ↓
Clinical Experience Engine
  ↓
React Renderer
```

O caminho oficial de consulta é `WS /api/v1/clinical-stream/{encounter_id}`,
que executa `LiveClinicalPipeline`. O Workbench reduz cada evento recebido em
uma `RuntimeSessionProjection`; a experiência clínica e a tela de revisão
usam essa projeção, inclusive o histórico de eventos A2UI.

Não existe mais um endpoint batch de consulta dentro do Runtime. O antigo
`POST /api/v1/mvp/consultations`, `CognitiveConsultationPipeline`,
`ClinicalJourneyExecutor` e os SDKs exclusivos desse caminho foram removidos
na estabilização SPR-002.

## Mapa de responsabilidades

| Boundary | Implementação ativa | Entrada/saída |
|---|---|---|
| Speech Runtime | `SpeechEnginePort` + `SpeechEngineSessionAdapter` | PCM → provider-neutral SpeechEvent |
| Transcript | `StreamingTranscriptState` / `ConversationMemory` | partials e finais |
| Clinical Runtime | `LiveClinicalPipeline` | transcript → fatos/contexto/raciocínio |
| Knowledge Runtime | `ClinicalKnowledgeLayer` | fatos → conhecimento |
| Presentation Runtime | `ClinicalPresentationComposer` | conhecimento → cards/timeline |
| A2UI Runtime | `ClinicalA2UIProjector` | presentation → JSONL A2UI |
| Runtime Session | `runtime-session.ts` | eventos → projeção única |
| Clinical Experience Engine | `A2UICognitiveRenderer` + estado da sessão | A2UI → experiência |
| React Renderer | `App.tsx` | projeção → tela |

## Providers

| Capability | Provider | Estado | Ativação |
|---|---|---|---|
| Speech | `XAIStreamingSpeechProvider` via `SpeechEnginePort` | ACTIVE | padrão em `ASTERA_SPEECH_PROVIDER=streaming`; `xai` é alias |
| Speech | `FasterWhisperTranscriber` via `SpeechEnginePort` | LEGACY | somente com `ASTERA_SPEECH_PROVIDER=faster-whisper` |
| Speech | `ParakeetNimTranscriber` via `SpeechEnginePort` | PLANNED | somente após validação do NIM |
| Clinical candidates | `KeywordClinicalNlp` | ACTIVE | instanciado pelo Runtime |
| Clinical facts | `DeterministicClinicalFactsExtractor` | ACTIVE | instanciado pelo Runtime |
| Clinical context | `DeterministicClinicalContextBuilder` | ACTIVE | instanciado pelo Runtime |
| Clinical reasoning | `DeterministicClinicalReasoner` | ACTIVE | padrão |
| Clinical reasoning | `GrokClinicalReasoner` | EXPERIMENTAL | somente com `ASTERA_COGNITIVE_PROVIDER=grok` |
| Knowledge | `ClinicalKnowledgeLayer` | ACTIVE | parte do live pipeline |
| Presentation | `ClinicalPresentationComposer` | ACTIVE | parte do live pipeline |
| A2UI | `ClinicalA2UIProjector` | ACTIVE | parte do live pipeline |

`GrokClinicalNlp` foi removido por não participar da cadeia ativa. Não há
provider de NLP batch paralelo.

## Endpoints

| Endpoint | Papel | Estado |
|---|---|---|
| `WS /api/v1/clinical-stream/{encounter_id}` | consulta clínica live | ACTIVE |
| `WS /api/v1/streaming/{stream_id}` | transporte genérico de eventos | ACTIVE / transporte |
| `GET /api/v1/clinical-review/encounters` | projeção downstream do live store | ACTIVE |
| `GET /api/v1/clinical-review/encounters/{encounter_id}` | projeção downstream do live store | ACTIVE |
| `GET /api/v1/a2ui/workspace` | documento A2UI de workspace | ACTIVE |
| `GET /api/v1/a2ui/encounters/{encounter_id}` | documento A2UI downstream | ACTIVE |
| `POST /api/v1/mvp/consultations` | pipeline batch antigo | REMOVED |

Os endpoints de Review e A2UI não iniciam uma consulta nem criam uma segunda
execução: somente leem projeções produzidas pelo `LiveClinicalPipeline`.

## Eventos do Runtime

O produtor oficial é `LiveClinicalPipeline`; o broker encaminha os eventos ao
Workbench; `speech-session.ts`, `runtime-session.ts` e
`A2UICognitiveRenderer` são os consumidores/transformadores; `App.tsx` é o
renderer final. A lista validada em SPR-002 inclui:

```text
consultation.pipeline.started
speech.started
transcript.created
transcript.partial
transcript.done
transcript.error
speech.realtime.metrics
speech.runtime.metrics
clinical.fast.<category>.detected
clinical.fact.detected
clinical.knowledge.event
clinical.knowledge.updated
clinical.runtime.status
clinical.deep.context.updated
clinical.deep.reasoning.started
clinical.deep.reasoning.updated
clinical.representation.updated
clinical.fhir.updated
clinical.deep.soap.updated
clinical.soap.updated
clinical.deep.completed
clinical.deep.error
a2ui.cognitive.stream
speech.stopped
consultation.pipeline.completed
consultation.pipeline.error
```

Aliases de eventos de pipelines anteriores (`fact.created`, `evidence.created`,
`context.updated`, `reasoning.updated`, `knowledge.updated`) não são mais
aceitos pelo Workbench.

## Workbench

As superfícies Consulta, Theater, Runtime, Clinical Experience e Revisão
Clínica recebem o mesmo stream WebSocket. A tela de Revisão não busca mais
`Review Snapshot`, não usa snapshots antigos e não possui um caminho de
reidratação batch. Sua fonte é a `RuntimeSessionProjection` atual, que é
alimentada pelos eventos A2UI e clínicos do Runtime.

## Fonte única da interface

`RuntimeSessionProjection` é a única fonte de verdade para dados clínicos e
de apresentação na interface. O único ponto que reduz eventos do Runtime é
`updateRuntimeSession`; o React apenas lê a projeção e renderiza suas
superfícies.

Estados locais continuam permitidos somente para controle de interface,
comunicação, mídia, navegação e edição do documento A2UI. Nenhuma tela pode
manter transcript, facts, knowledge, context, reasoning, SOAP, FHIR,
presentation ou A2UI clínico derivados diretamente do stream.

O caminho obrigatório é:

```text
Runtime events
  ↓
updateRuntimeSession
  ↓
RuntimeSessionProjection
  ↓
React Renderer
  ↓
Clinical Experience / Theater / Timeline / Runtime / Clinical Tab
```

## Regra de evolução

Uma mudança clínica somente está integrada quando percorre o Runtime inteiro,
tem publisher/consumer/renderer identificado, possui teste no live path e
aparece na `RuntimeSession`. Código que não participa desse caminho deve ser
removido ou documentado como LEGACY; não pode ser uma segunda implementação
ativa.

A arquitetura do Runtime está encerrada como baseline. O trabalho seguinte é
validação e evolução de produto: Speech Runtime, Clinical Experience, Evidence
Engine, Reasoning Engine e Clinical Copilot. Nenhuma nova sprint arquitetural
deve ser aberta sem um ADR aprovado.

O resultado da estabilização anterior está em
`docs/engineering/ASTERA-SPR-002-runtime-stabilization.md`; a consolidação da
fonte única da interface e os bloqueios finais estão em
`docs/engineering/ASTERA-SPR-004-runtime-session-consolidation.md`.
