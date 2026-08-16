# ASTERA-SPR-004 — Runtime Session Consolidation

Status: `READY FOR PRODUCT VALIDATION`

Architecture status: `READY`

Product status: `PENDING VALIDATION`

Data: 2026-08-10

## Decisão arquitetural

`READY FOR PRODUCT VALIDATION`

A consolidação estrutural foi implementada e os builds automatizados passam.
O SPR-004 encerra o trabalho arquitetural. Permanecem como validações de
produto e infraestrutura:

1. uma consulta real com áudio clínico que atravesse Facts → Knowledge →
   Presentation → RuntimeSessionProjection;
2. um alvo de Desktop do Astera para executar o build quando essa aplicação
   fizer parte do produto.

Esses itens não bloqueiam a arquitetura consolidada; bloqueiam apenas a
validação funcional completa do produto.

## Resultado da consolidação

O Workbench agora possui um único estado clínico de React:

```text
Runtime events
  ↓
App.handleRuntimeEvent
  ↓
updateRuntimeSession
  ↓
RuntimeSessionProjection
  ↓
React Renderer
  ↓
Clinical Experience / Theater / Timeline / Runtime / Clinical Tab
```

`updateRuntimeSession` é o único redutor que transforma eventos em transcript,
facts, context, reasoning, knowledge, SOAP, FHIR, apresentação, métricas e
histórico. As superfícies recebem a mesma projeção.

Arquivos principais:

- `astera-workbench/src/runtime-session.ts`: projeção e redutor único;
- `astera-workbench/src/App.tsx`: uma única `runtimeProjection` no topo e
  renderização derivada dela;
- `astera-workbench/src/clinical-stream.ts`: áudio envia métricas de volta ao
  Runtime por evento, sem callback direto para React;
- `docs/runtime/RUNTIME.md`: regra oficial de fonte única da interface.

## Etapa 1 — Estados relacionados à consulta

| Estado | Cria/atualiza | Consome | Classificação |
|---|---|---|---|
| `runtimeProjection` | `App.handleRuntimeEvent` → `updateRuntimeSession` | Todas as telas clínicas | Fonte canônica |
| Speech/transcript | `runtime-session.ts` via `speech-session.ts` | React Renderer | Dentro da projeção |
| Facts/context/reasoning/knowledge | `runtime-session.ts` | React Renderer | Dentro da projeção |
| Presentation/A2UI | `runtime-session.ts` + `A2UICognitiveRenderer` | Theater, Clinical Experience e Runtime | Dentro da projeção |
| câmera, microfone, conexão, timers e lifecycle da consulta | componentes de comunicação/mídia | controles de UI | Estado local permitido |
| schema/documento A2UI, abas, validação e posição do player | `A2UIPreview` | editor/renderer de documento | Estado de ferramenta, não clínico |
| navegação, tema, autenticação e seleção de arquivo | `App.tsx` | shell da aplicação | Estado de UI, não clínico |

Não restou `useState`, `useReducer`, store, signal, ref, buffer ou snapshot
local representando transcript, facts, knowledge, context, reasoning, SOAP,
FHIR, Presentation ou A2UI clínico.

## Etapa 2 — Dependências

O produtor de eventos é o `LiveClinicalPipeline`. O Workbench possui uma única
entrada de eventos (`handleRuntimeEvent`) e um único redutor (`updateRuntimeSession`).
Não há consumidor clínico alternativo em Theater, Clinical Experience, Timeline,
Runtime Tab ou Clinical Tab.

## Etapas 3 e 4 — Caminhos diretos e testes

As superfícies não recebem mais eventos de Speech, Clinical ou Presentation
diretamente. O `ClinicalAudioStream` publica áudio e métricas no WebSocket; a
resposta entra em `handleRuntimeEvent` e só então chega ao React através da
projeção.

Validação automatizada executada:

```text
Backend compileall: PASS
Backend pytest:     126 passed, 4 warnings
Workbench build:    PASS (tsc -b && vite build)
```

O warning do Vite sobre tamanho do bundle é informativo e não falha o build.

## Etapa 5 — Telas

| Tela/superfície | Fonte clínica |
|---|---|
| Clinical Experience | `runtimeProjection.presentation` e campos da projeção |
| Theater / A2UI | `runtimeProjection` + documento A2UI de schema |
| Timeline | `runtimeProjection.events` / `presentation.timeline` |
| Runtime Tab | `runtimeProjection.events`, status e payloads |
| Clinical Tab | `runtimeProjection` |
| Clinical Review | `runtimeProjection`, sem Review Snapshot ou busca batch |

O adaptador visual anterior de Review foi removido. A tela de revisão lê
diretamente os campos da `RuntimeSessionProjection`; dados ausentes permanecem
ausentes e não são preenchidos localmente.

## Etapa 6 — Grafo de Runtime

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
RuntimeSessionProjection
  ↓
React Renderer
  ↓
Clinical Experience
```

O grafo está refletido no código ativo. A projeção substitui o estado clínico
paralelo que existia em Theater/Clinical Experience.

## Etapa 7 — Prova de runtime

Foi executado um WebSocket real contra:

```text
/api/v1/clinical-stream/spr004-real-audio-2
```

Resultado observado: 29 eventos reais, incluindo `speech.started`,
`consultation.pipeline.started`, `transcript.created`, `transcript.done`,
`a2ui.cognitive.stream`, `clinical.runtime.status`, `speech.stopped` e
`consultation.pipeline.completed`. Transcript e A2UI foram confirmados.

O único áudio disponível para essa execução era um arquivo de sistema não
clínico. Por isso não houve `clinical.fact.detected` nem atualização de
Knowledge/representações clínicas. Essa execução prova o transporte e a
projeção parcial, mas não satisfaz a prova clínica ponta a ponta exigida pelo
SPR-004.

## Etapa 8 — Builds

Backend e Workbench compilam e passam suas validações acima.

Não existe projeto Desktop do Astera neste workspace: não há `Cargo.toml`,
`.csproj`, configuração Tauri ou configuração Electron associada ao produto.
Consequentemente, o build Desktop obrigatório não pode ser executado.

## Etapa 9 — Drift

| Drift | Resultado atual | Observação |
|---|---:|---|
| Architecture Drift | 0 no caminho auditado | fluxo único implementado |
| Runtime Drift | 0 no Workbench auditado | uma entrada e um redutor |
| Provider Drift | 0 na matriz existente | Faster Whisper ativo; Parakeet experimental |
| Event Drift | 0 no consumidor auditado | eventos entram pelo redutor único |
| Projection Drift | 0 no código auditado | validação funcional clínica ainda pendente |

## Validações de produto pendentes

| Módulo | Arquivo/escopo | Motivo |
|---|---|---|
| Clinical Experience / Theater | fixture/ambiente de execução | falta áudio clínico real para validar Facts → Knowledge → Presentation |
| Desktop | workspace do Astera | não existe alvo de Desktop; infraestrutura ainda não está no escopo executável |

## Critério arquitetural — atingido

O SPR-004 é considerado arquiteturalmente concluído porque:

1. não há estado clínico paralelo nas telas auditadas;
2. todas as telas clínicas consomem `RuntimeSessionProjection`;
3. o Runtime possui uma entrada e um redutor de projeção;
4. Backend e Workbench compilam e passam os testes disponíveis;
5. o fluxo real já provou Speech → Transcript → A2UI → Projection → React.

As validações de áudio clínico, consulta completa, áudio degradado, consulta
longa, interrupção, troca de paciente e Desktop pertencem à fase
`PRODUCT VALIDATION`, não a uma nova sprint arquitetural.
