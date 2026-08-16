---
document_id: astera-spr-001-runtime-validation
title: ASTERA-SPR-001 — Runtime Validation
category: Engineering
status: PROPOSED
version: 1.0
owner: Astera Engineering
depends_on:
  - ../runtime/RUNTIME.md
  - ./ASTERA-ENG-002-runtime-audit.md
  - ./ASTERA-ENG-004-execution-trace.md
  - ./ASTERA-ENG-006-end-to-end-validation.md
used_by:
  - Runtime Engineering
  - Release Gate
last_updated: 2026-08-10
---

# ASTERA-SPR-001 — Runtime Validation

## Objetivo

Validar que o Runtime descrito em [`docs/runtime/RUNTIME.md`](../runtime/RUNTIME.md)
representa todo o sistema.

Nenhuma alteração funcional será feita nesta validação. Nenhum código novo será
criado. A missão é provar que todos os módulos do Astera conseguem ser
conectados ao Runtime e que não existe um caminho paralelo oculto.

O estado permanece **PROPOSED** até que todas as etapas abaixo tenham evidência
registrada.

## Etapa 1 — Responsabilidades dos módulos

Para cada módulo, registrar quem instancia, quem chama, quem consome e quem
finaliza:

| Módulo | Instancia | Chama | Consome | Finaliza | Evidência |
|---|---|---|---|---|---|
| Speech | ☐ | ☐ | ☐ | ☐ | ☐ |
| Clinical | ☐ | ☐ | ☐ | ☐ | ☐ |
| Knowledge | ☐ | ☐ | ☐ | ☐ | ☐ |
| Presentation | ☐ | ☐ | ☐ | ☐ | ☐ |
| A2UI | ☐ | ☐ | ☐ | ☐ | ☐ |
| Runtime Session | ☐ | ☐ | ☐ | ☐ | ☐ |
| React Renderer | ☐ | ☐ | ☐ | ☐ | ☐ |
| Workbench | ☐ | ☐ | ☐ | ☐ | ☐ |

## Etapa 2 — Grafo de dependências

Construir e registrar o grafo completo de dependências.

Critérios:

- nenhum módulo pode ficar isolado;
- nenhum módulo pode possuir caminho alternativo para uma consulta clínica;
- cada aresta deve apontar para o boundary responsável no Runtime.

```text
Player
  ↓
Speech Runtime
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

## Etapa 3 — Endpoints

Validar todos os endpoints. Cada endpoint deve registrar o Runtime utilizado.
Se utilizar outro caminho, marcar explicitamente como **LEGACY**.

| Endpoint | Runtime utilizado | Consumidor | Status | Evidência |
|---|---|---|---|---|
| `WS /api/v1/clinical-stream/{encounter_id}` | ☐ | ☐ | ☐ | ☐ |
| `WS /api/v1/streaming/{stream_id}` | ☐ | ☐ | ☐ | ☐ |
| `POST /api/v1/mvp/consultations` | ☐ | ☐ | **LEGACY** | ☐ |
| Demais endpoints | ☐ | ☐ | ☐ | ☐ |

## Etapa 4 — Testes

Validar todos os testes. Cada teste deve registrar o Runtime utilizado e sua
classificação quando cobrir o caminho legado.

| Teste/suíte | Runtime utilizado | Status | LEGACY? | Evidência |
|---|---|---|---|---|
| `apps/runtime/tests/` | ☐ | ☐ | ☐ | ☐ |
| `astera-workbench/src/` | ☐ | ☐ | ☐ | ☐ |

Um teste verde no caminho legado não comprova a execução do Runtime.

## Etapa 5 — Telas

Validar todas as telas e registrar a origem dos dados. Nenhuma tela pode usar
snapshot antigo ou pipeline paralelo como fonte de execução.

| Tela | Origem dos dados | Runtime utilizado | Snapshot antigo? | Pipeline paralelo? | Evidência |
|---|---|---|---|---|---|
| Clínica | ☐ | ☐ | ☐ | ☐ | ☐ |
| Theater / Player | ☐ | ☐ | ☐ | ☐ | ☐ |
| Runtime Tab | ☐ | ☐ | ☐ | ☐ | ☐ |
| Clinical Experience | ☐ | ☐ | ☐ | ☐ | ☐ |
| Review | ☐ | ☐ | ☐ | ☐ | ☐ |
| Demais telas | ☐ | ☐ | ☐ | ☐ | ☐ |

## Etapa 6 — Matriz de integração

| Módulo | Runtime | Integrado | Executando | Evidência |
|---|---|---|---|---|
| Speech | ☐ | ☐ | ☐ | ☐ |
| Clinical | ☐ | ☐ | ☐ | ☐ |
| Knowledge | ☐ | ☐ | ☐ | ☐ |
| Presentation | ☐ | ☐ | ☐ | ☐ |
| A2UI | ☐ | ☐ | ☐ | ☐ |
| Runtime Session | ☐ | ☐ | ☐ | ☐ |
| Clinical Experience Engine | ☐ | ☐ | ☐ | ☐ |
| React Renderer | ☐ | ☐ | ☐ | ☐ |
| Workbench | ☐ | ☐ | ☐ | ☐ |

## Etapa 7 — Verificação de desvios

Responder objetivamente:

> Existe qualquer caminho que contorne `StreamingTranscriptState` → `Clinical
> Runtime` → `Presentation Runtime` → `A2UI Runtime` → `Runtime Session`?

Resultado: **PENDENTE**.

Se existir, listar o caminho, o ponto de entrada, os consumidores, os testes e
classificá-lo como **LEGACY** antes de qualquer remoção.

## Etapa 8 — Consulta real

Executar uma consulta real e registrar um Execution Trace com evidência de cada
etapa:

```text
Player
  ↓
Speech Runtime
  ↓
Transcript
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
  ↓
Tela
```

Resultado: **PENDENTE**. Todas as etapas devem ser confirmadas como executadas;
transporte, teste sintético ou snapshot isolado não substituem a consulta real.

## Critério de aceite

Somente após a conclusão das oito etapas, com evidências anexadas, o Runtime
será considerado validado. Antes disso, ele permanece **PROPOSED**.

A remoção de `CognitiveConsultationPipeline` só poderá começar depois de:

- todos os consumidores públicos terem sido inventariados;
- todos os endpoints e testes legados terem sido marcados;
- nenhum caminho de execução oculto ter sido encontrado;
- a consulta real ter percorrido o fluxo completo até a tela.

## Resultado da execução — 2026-08-10

### Evidências executadas

| Evidência | Resultado |
|---|---|
| Runtime Python — `pytest -q` | **132 passed, 6 warnings** em 13,51 s |
| Workbench — `npm run build` | **Passou**: `tsc -b` + Vite, 2.183 módulos transformados |
| Workbench — render headless | **Passou**: React montou a superfície de Consulta Clínica |
| Runtime — `/health`, `/live`, `/status` | **Passou**: `alive`, `alive`, `ready` |
| Kernel | **READY** no Runtime isolado em `127.0.0.1:8010` |
| WebSocket live com áudio de teste | **29 eventos**, Faster-Whisper executando, transcript e encerramento observados |
| Live Clinical Pipeline com fixture clínica | **63 eventos**, incluindo facts, Knowledge, representações, A2UI e encerramento |
| Consulta clínica real reproduzível até React | **PENDENTE**: não havia gravação clínica disponível no ambiente |
| Testes Deno do Workbench | **NÃO EXECUTADOS**: Deno indisponível; `npm test` não existe no `package.json` |

### ASTERA RUNTIME REPORT

```text
=========================
ASTERA RUNTIME REPORT
=========================

Pipeline do Runtime

PROPOSTO — NÃO VALIDADO

Speech Runtime

EXECUTANDO
Evidência: WebSocket real + Faster-Whisper + transcript.done.

StreamingTranscriptSession

PARCIAL
O ciclo de sessão existe no adapter live e no Workbench; não há uma classe
backend com esse nome. O boundary permanece conceitual.

StreamingTranscriptState

EXECUTANDO
Evidência: ConversationMemory herda StreamingTranscriptState e a execução
live publicou transcript.created, transcript.done e speech.stopped.

Clinical Runtime

EXECUTANDO
Evidência: LiveClinicalPipeline emitiu clinical.fast.*, clinical.deep.* e
consultation.pipeline.completed na fixture clínica.

Knowledge Runtime

EXECUTANDO
Evidência: clinical.knowledge.event e clinical.knowledge.updated.

Presentation Runtime

EXECUTANDO
Evidência: clinical.representation.updated, clinical.fhir.updated e
clinical.deep.soap.updated; representações summary/soap/fhir presentes.

A2UI Runtime

EXECUTANDO
Evidência: a2ui.cognitive.stream no WebSocket real e na fixture clínica.

Runtime Session

PARCIAL
O reducer updateRuntimeSession está compilado e é alimentado pelos handlers
live do Workbench. A execução observada não comprovou o evento live chegando
à projeção React durante uma consulta clínica real.

Clinical Experience Engine

PARCIAL
A superfície ClinicalExperienceView existe e é montada pelo Workbench, mas a
consulta real clínica até essa superfície permanece pendente.

React Renderer

EXECUTANDO
Evidência: npm run build passou e o Chrome headless montou o DOM da Consulta
Clínica a partir do bundle produzido.

Workbench

EXECUTANDO
Evidência: build TypeScript/Vite e render headless passaram.

-------------------------

Pipelines Legados

1
↓
CognitiveConsultationPipeline
Status
QUARENTENA — ainda instanciado por journey_factory() e publicado em
POST /api/v1/mvp/consultations.

2
↓
ConsultationPipeline
Status
NÃO CONECTADO AO BOOTSTRAP — permanece importável e coberto por teste.

-------------------------

Código Morto

NÃO REMOVIDO

FASE 2 não iniciada. Não foi feita contagem nem remoção nesta validação.

-------------------------

Providers

Speech

Faster Whisper
ACTIVE — provider utilizado pelo Runtime live nesta execução.

Parakeet
EXPERIMENTAL/INACTIVE — adapter existe, mas 127.0.0.1:9000 respondeu como
MinIO (403), não como Parakeet NIM.

Cognitive

KeywordClinicalNlp
ACTIVE no live fast path.

DeterministicMedicalNlp / GrokClinicalNlp
CONFIGURÁVEIS no caminho batch; não equivalem ao provider live atual.

-------------------------

Runtime Drift

DETECTADO — caminho batch paralelo ainda publicado.

Architecture Drift

DETECTADO — o Runtime documentado exige uma cadeia única, mas o bootstrap
instancia dois caminhos clínicos.

Provider Drift

DETECTADO — live e batch usam boundaries/providers cognitivos diferentes.

Event Drift

DETECTADO — o contrato esperado menciona speech.done, mas a execução usa
transcript.done e speech.stopped.

Projection Drift

DETECTADO — existem projeções live, Review downstream e snapshots locais de
replay; sua equivalência end-to-end não foi provada.

-------------------------

STATUS

BLOCKED — SPR-001 INCOMPLETO
NÃO PRONTO PARA DESENVOLVIMENTO
```

### Grafo observado

```text
Player / Workbench
  ↓
ClinicalFileAudioStream ou ClinicalAudioStream
  ↓
WS /api/v1/clinical-stream/{encounter_id}
  ↓
LiveClinicalPipeline
  ↓
ConversationMemory : StreamingTranscriptState
  ↓
FasterWhisperTranscriber
  ↓
Clinical facts / Knowledge / Presentation / A2UI
  ↓
InMemoryStreamBroker
  ├── Review projector → ClinicalReviewResultStore
  └── WebSocket → App.tsx → Runtime Session → Clinical Experience

CAMINHO PARALELO ENCONTRADO

POST /api/v1/mvp/consultations
  ↓
journey_factory()
  ↓
ClinicalJourneyExecutor
  ↓
CognitiveConsultationPipeline
```

### Etapa 7 — resposta

**Sim.** Existe um caminho que contorna o fluxo live: `POST
/api/v1/mvp/consultations` → `ClinicalJourneyExecutor` →
`CognitiveConsultationPipeline`. Ele está listado como **LEGACY/QUARENTENA**;
nenhuma remoção foi executada.

Também existe `ConsultationPipeline` em
`apps/runtime/src/application/clinical/consultation.py`, não conectado ao
bootstrap atual, mas ainda importável e coberto por teste.

### Etapa 8 — resposta

O WebSocket real percorreu:

```text
Player-equivalente (cliente WebSocket)
  → Speech Runtime
  → Transcript
  → A2UI Runtime
  → Speech stopped
  → Runtime completed
```

A fixture clínica percorreu adicionalmente:

```text
Clinical
  → Knowledge
  → Presentation
  → A2UI
```

Falta uma consulta clínica real, reproduzível e observada até `Runtime Session`
e `React Renderer`. Portanto, a Etapa 8 permanece **PENDENTE para aceite**.

## Decisão da FASE 1

A FASE 1 produziu evidência suficiente para classificar os componentes do
Runtime, mas **não foi aprovada**. A FASE 2 — limpeza — permanece bloqueada.

Não remover:

- `CognitiveConsultationPipeline`;
- `ConsultationPipeline`;
- providers;
- eventos;
- reducers;
- snapshots;
- qualquer pipeline duplicado.

Próximas evidências necessárias para encerrar o SPR-001:

1. executar uma consulta clínica real com áudio de fala reproduzível;
2. registrar o trace completo até a tela React;
3. definir formalmente a compatibilidade entre os eventos esperados e os
   eventos observados;
4. inventariar todos os consumidores do caminho legado antes da FASE 2.
