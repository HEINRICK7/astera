---
document_id: astera-sprint-000-runtime-alignment
title: ASTERA-SPRINT-000 — Platform Stabilization & Runtime Alignment
category: Engineering
status: Audit Report
version: 1.0
owner: Astera Engineering
depends_on:
  - ./ASTERA-ENG-002-runtime-audit.md
  - ./ASTERA-ENG-003-runtime-integration-contract.md
  - ./ASTERA-ENG-004-execution-trace.md
  - ./ASTERA-ENG-005-provider-governance.md
  - ./ASTERA-ENG-006-end-to-end-validation.md
  - ./ASTERA-ENG-007-runtime-observability.md
  - ./ASTERA-ENG-008-architecture-drift.md
  - ./ASTERA-ENG-009-source-of-truth.md
  - ./ASTERA-ENG-010-release-gate.md
last_updated: 2026-08-10
---

# ASTERA-SPRINT-000 — Platform Stabilization & Runtime Alignment

## Veredito

**BLOQUEADO.**

O alinhamento do caminho live foi corrigido e comprovado por testes de
integração, build do Workbench e smoke test do WebSocket real. A Sprint não
pode ser aprovada porque o provider de Speech ativo continua sendo
Faster-Whisper `base`, executado em janelas fixas de 3 segundos, emitindo
somente segmentos finais. Em consulta real observada no Workbench, isso deixa
`partial_events = 0` e `revision_count = 0`.

Não houve criação de feature clínica nova. As alterações desta Sprint são de
integração, projeção, observabilidade de fluxo e remoção de caminho morto do
Workbench.

## Escopo auditado

O checkout auditado contém:

- Runtime Python em `apps/runtime`;
- Workbench Deno/Desktop em `/home/carlos-henrique/Documentos/workspace/astera-workbench`;
- SDKs compartilhados em `packages`;
- Constituição de Engenharia e ADRs em `docs`;
- Runtime ativo em `127.0.0.1:8001`;
- processo Deno/Desktop ativo, apontando para `http://127.0.0.1:8001`.

Há alterações e arquivos não rastreados preexistentes no checkout. Este
relatório não reverteu nem apagou esse trabalho; classifica o que está no
caminho de execução atual.

O Runtime definido nesta etapa está em
[RUNTIME](../runtime/RUNTIME.md). A validação formal do Runtime está registrada
em [ASTERA-SPR-001 — Runtime Validation](./ASTERA-SPR-001-runtime-validation.md).

## Evidências executadas

| Evidência | Resultado |
|---|---|
| `GET http://127.0.0.1:8001/health` | `200`, `{"status":"alive"}` |
| Workbench `npm run build` | passou; `tsc -b` e `vite build` concluídos |
| Runtime `.venv/bin/python -m pytest -q` | `132 passed, 6 warnings` |
| Teste live direcionado | `3 passed`; lifecycle, Review e FHIR verificados |
| Smoke WebSocket real com PCM | 5 eventos; endpoint executou e encerrou sem erro |
| Smoke WebSocket com silêncio | nenhum `partial`/`done`; não é consulta clínica válida |
| Provider em `:9000` | respondeu como MinIO `403`, não como Parakeet NIM |

O smoke com silêncio prova transporte, sessão e encerramento. Não prova
qualidade de ASR. As imagens fornecidas do Workbench são evidência de consulta
real anterior e mostram os encontros `encounter-589ea9fa97d8` e
`encounter-b9013d9ff719`: múltiplos finais, zero partials e zero revisões.

## Fluxo Runtime efetivamente ativo

```text
Arquivo selecionado / áudio WebRTC
        ↓
ClinicalFileAudioStream ou ClinicalAudioStream
        ↓  PCM 16 kHz por WebSocket
/api/v1/clinical-stream/{encounter_id}
        ↓
LiveClinicalPipeline
        ↓
ConversationMemory : StreamingTranscriptState
        ↓
FasterWhisperTranscriber.transcribe_pcm_stream
        ↓
transcript.done  [caminho real atual]
        ↓
KeywordClinicalNlp
        ↓
DeterministicClinicalFactsExtractor
        ↓
ClinicalKnowledgeLayer + KeywordRetriever
        ↓
ClinicalContextBuilder + ClinicalReasoner
        ↓
KnowledgeRepresentationEngine
        ↓
clinical.representation.updated / clinical.fhir.updated / SOAP
        ↓
ClinicalA2UIProjector + ClinicalPresentationComposer
        ↓
InMemoryStreamBroker
        ├── WebSocket → App.tsx → RuntimeSession → tela Clínica
        └── Review projector → ClinicalReviewResultStore → Review
```

O Workbench seleciona o mesmo caminho live para reprodução de arquivo. O
antigo `runConsultation()` do Workbench foi removido do fluxo ativo; a função
antiga apontava para `/api/v1/mvp/consultations`.

## Fluxo paralelo ainda existente

```text
POST /api/v1/mvp/consultations
        ↓
journey_factory()
        ↓
ClinicalJourneyExecutor
        ↓
CognitiveConsultationPipeline
        ↓
transcriber.transcribe(audio completo)
        ↓
facts → context → reasoning → knowledge → representations
```

Esse endpoint continua exposto pelo Runtime e `src/runtime-client.ts` ainda
possui o método genérico correspondente. Ele não é mais chamado pelo fluxo de
consulta de arquivo do Workbench, mas ainda é um pipeline paralelo e, por
isso, impede o gate “sem pipeline antigo”.

## Integração por módulo

| Módulo | Arquivo/ponto de execução | Estado observado |
|---|---|---|
| Speech transport | `astera-workbench/src/clinical-stream.ts:51-183,186-280` | ✅ PCM contínuo chega ao WebSocket |
| Speech session | `apps/runtime/src/application/clinical/live_stream.py:51-78,368` | ✅ `ConversationMemory` usa `StreamingTranscriptState` |
| ASR ativo | `apps/runtime/src/adapters/speech/faster_whisper.py:73-155` | 🟡 executa, mas em janelas fixas e sem partial |
| Partial/revision | `packages/speech_sdk/models.py:192-340` e `live_stream.py:700-735` | 🟡 contrato existe; provider real não produz |
| Clinical fast path | `live_stream.py:749-851` | ✅ fatos, cards, conhecimento e métricas são emitidos |
| Clinical deep path | `live_stream.py:532-668` | ✅ contexto, reasoning, SOAP e representações são emitidos |
| Knowledge | `live_stream.py:789-830` + `knowledge_layer.py` | ✅ atualizado no caminho live sintético/integrado |
| Presentation | `presentation_composer.py` | ✅ compõe estados incrementais |
| A2UI | `a2ui_stream.py` + `live_stream.py:416-427` | ✅ JSONL publicado incrementalmente |
| React/Workbench | `astera-workbench/src/App.tsx:269-331,625-679` | ✅ consome eventos e atualiza Runtime Session |
| Review | `live_stream.py:80-258,402-414` | ✅ projeção downstream recebe lifecycle desde o primeiro evento |
| FHIR | `live_stream.py:592-611` + `App.tsx:302-304,672` | ✅ exposto no evento e na sessão viva |

## Governança de providers

| Capacidade | Provider/configuração | Estado | Prova |
|---|---|---|---|
| Speech | Faster-Whisper `base`, `development` | ACTIVE | `main.py:269-276`; settings atuais |
| Speech realtime | Parakeet NIM | EXPERIMENTAL/INACTIVE | adapter existe em `parakeet.py:134-340`, mas `:9000` é MinIO |
| NLP do pipeline batch | Grok | ACTIVE no batch | `main.py:278-307` |
| NLP do live fast path | `KeywordClinicalNlp` | ACTIVE no live | `main.py:309-319` |
| Reasoning | Grok | ACTIVE configurado | `main.py:278-286,317` |
| Facts/context | determinísticos | ACTIVE | `main.py:298-301,315-316` |
| Knowledge | `KeywordRetriever` + `InMemoryKnowledgeStore` | ACTIVE development | `main.py:254-255` |
| Representation/FHIR | `KnowledgeRepresentationEngine` + `InMemoryFhirGateway` | ACTIVE development | `main.py:253-255,303-306` |
| Event transport | `InMemoryStreamBroker` no live; NATS no Kernel | ACTIVE development | `main.py:212-213,309`; `main.py:190-193` |

Existe uma divergência de provider cognitivo: `cognitive_provider=grok`
configura Grok para o pipeline batch, enquanto o live fast path usa
`KeywordClinicalNlp`. Ambos não são providers equivalentes para auditoria de
resultado clínico; a distinção precisa permanecer registrada até a integração
ser unificada.

## Requisitos dos ADRs e classificação

| Requisito | Classificação | Evidência objetiva |
|---|---|---|
| Streaming PCM contínuo | 🟡 Implementado mas não conforme o contrato completo | Workbench envia PCM incremental; ASR fatia em `window_bytes` |
| `StreamingTranscriptState` | ✅ Implementado e executando | `ConversationMemory` herda e é instanciada no live |
| `StreamingTranscriptSnapshot` | ✅ Implementado e executando no encerramento | `speech.stopped` publica `freeze().to_dict()` |
| `speech.started` | ✅ Implementado e executando | primeiro evento do teste live |
| `speech.partial` | 🟡 Implementado no contrato, não executando com provider ativo | reducer e pipeline aceitam partial; smoke real teve zero |
| `transcript.done` | ✅ Implementado e executando quando ASR retorna final | emitido pelo loop live |
| `speech.done` | 🔴 Não implementado como evento com esse nome | existe `transcript.done`, não `speech.done` |
| `speech.stopped` | ✅ Implementado e executando | último ciclo do smoke real |
| Revisão incremental | 🟡 SDK implementa; ASR ativo não revisa | Workbench real mostrou `revision_count = 0` |
| Partial buffer | ✅ Estado existe e é atualizado quando há partial | `current_partial` em state/store |
| Final buffer | ✅ Estado existe e é atualizado | `final_segments` e `full_transcript` |
| IDs estáveis | 🟡 fallback existe; Faster-Whisper não fornece identidade ASR | `segment_id` é sintetizado pelo SDK |
| Contexto contínuo no Clinical Runtime | ✅ executando | `rolling_text` e `memory_window=rolling-30s` |
| Contexto contínuo no ASR | 🔴 não executando | cada janela chama `transcribe()` independente |
| Janelas fixas | 🔴 ainda ativas | `faster_whisper.py:94-155`, settings `3.0s` |
| VAD | ✅ executando | `vad_filter=True` em `faster_whisper.py:212` |
| Endpointing | 🔴 não observado no provider ativo | encerramento depende de `stop`/flush |
| Rolling context | 🟡 apenas Clinical Runtime | não é enviado ao ASR |
| Revisão de segmentos antigos | 🔴 não executando no provider ativo | cada final recebe nova sequência |
| Latência ponta a ponta | 🟡 métricas existem, trace real não completou todas | campos em `_live_metrics()`; smoke sem final |
| Telemetria | ✅ parcialmente executando | logs `clinical.stream event=...`, métricas e observability em memória |
| Speech Metrics | 🟡 parcial | bytes/chunks/latências existem; silêncio/fala e min/máx não estão completos |
| A2UI dependente de Speech | ✅ executando no live integrado | `a2ui.cognitive.stream` aparece antes do deep reasoning no teste |
| Review downstream | ✅ no caminho live | fila de projeção é criada antes de `speech.started` |
| React consome Runtime vivo | ✅ para Clínica/Teatro | `handleTheaterEvent` e `handleClinicalEvent` atualizam `RuntimeSession` |
| Review consome snapshot | ✅ apenas na tela Review | snapshot é projeção congelada/replay, não fonte do live |
| Clínica depende de Review | ✅ removido no fluxo live de arquivo | Theater não faz reidratação final via `getClinicalReview()` |

## Eventos observados

### Smoke real do Runtime

```text
speech.started
consultation.pipeline.started
transcript.created
speech.stopped
consultation.pipeline.completed
```

O áudio usado foi silêncio; a ausência de `transcript.partial` e
`transcript.done` nesse caso é esperada e não foi contada como sucesso clínico.

### Teste live integrado com transcriber fragmentado

```text
speech.started
consultation.pipeline.started
transcript.created
speech.audio.received
transcript.done / transcript.partial [dependente do provider]
clinical.fast.symptom.detected
clinical.fact.detected
clinical.knowledge.event
clinical.knowledge.updated
clinical.runtime.status
speech.runtime.metrics
clinical.deep.context.updated
clinical.deep.reasoning.started
clinical.deep.reasoning.updated
clinical.representation.updated
clinical.fhir.updated
clinical.deep.soap.updated
clinical.soap.updated
clinical.deep.completed
a2ui.cognitive.stream
speech.stopped
consultation.pipeline.completed
```

O teste direcionado confirmou ainda que `review.events[0]` é
`speech.started`, que `representations` contém `summary`, `soap` e `fhir`, e
que o `clinical.fhir.updated` é emitido.

`transcript.partial` aparece no contrato e no teste de infraestrutura quando
um provider o fornece, mas não foi observado nas consultas reais do
Faster-Whisper ativo.

## Divergências e código morto encontrado

1. **Pipeline batch legado ainda publicado:**
   `apps/runtime/src/adapters/http/mvp.py:41-100` chama
   `CognitiveConsultationPipeline` com áudio completo.
2. **Cliente batch legado ainda existe:** `astera-workbench/src/runtime-client.ts`
   mantém `submitConsultation()` para `/api/v1/mvp/consultations`; o fluxo
   principal não o chama depois do alinhamento.
3. **Pipeline antigo não conectado ao bootstrap atual:**
   `apps/runtime/src/application/clinical/consultation.py:13-68` existe e é
   coberto por testes, mas não é instanciado pelo bootstrap ativo.
4. **Parakeet não está ativo:** adapter implementado, endpoint configurado
   para uma porta que atualmente é MinIO.
5. **Plugin registry não representa todos os adapters clínicos:** o bootstrap
   registra `EchoPlugin`; Speech, Clinical, Knowledge e A2UI são instanciados
   diretamente fora do registry.
6. **Telemetria de áudio não chega ao Workbench:**
   `streaming.py:50-57` deliberadamente não encaminha `speech.audio.received`;
   o Review interno recebe o evento.
7. **Provider cognitivo dividido:** Grok no batch e Keyword no live fast path.
8. **Evento `speech.done` ausente:** o sistema usa `transcript.done` e
   `speech.stopped`.
9. **Real ASR sem revisão:** o provider ativo retorna `is_final=True` para os
   segmentos produzidos e não fornece partial, item id ou revisão do mesmo
   segmento.

Não foram removidos adapters ou pipelines legados nesta Sprint porque eles
ainda possuem referências públicas/testes. Eles estão classificados como
paralelos/não ativos, não como parte falsa do caminho live.

## Alterações de alinhamento realizadas

- Workbench de arquivo passou a usar `ClinicalFileAudioStream` e o WebSocket
  live, removendo a chamada ativa ao endpoint batch.
- Workbench deixou de buscar o Review Snapshot ao terminar a reprodução; a
  fonte da sessão é o `RuntimeSession` alimentado pelos eventos live.
- `RuntimeSession` passou a carregar FHIR junto de Speech, Facts, Context,
  Reasoning, Knowledge, SOAP, Workspace e A2UI.
- O projector do Review é iniciado antes de `speech.started`, preservando o
  lifecycle completo desde o primeiro evento.
- O live pipeline publica as representações existentes e o evento
  `clinical.fhir.updated`.
- FHIR passou a ser atualizado no estado vivo do Theater/Clínica.
- Funções do antigo submit batch foram removidas do fluxo ativo do Workbench.
- O teste live passou a provar lifecycle, projeção downstream e FHIR.

## Gate final da Sprint 000

| Critério | Resultado |
|---|---|
| Runtime usa o fluxo live novo | ✅ para WebSocket e reprodução de arquivo |
| React consome Runtime vivo | ✅ Clínica/Teatro |
| Review é downstream | ✅ no caminho live |
| Clinical/Knowledge/Presentation/A2UI executam | ✅ comprovado no teste integrado |
| Speech partial/revision reais | ❌ não comprovado; provider ativo não entrega |
| Pipeline antigo removido | ❌ ainda exposto no endpoint MVP |
| Código morto/paralelo eliminado | ❌ ainda há adapters, endpoint e cliente legado |
| Consulta real completa sem mocks | ❌ não validada neste turno com áudio falado reproduzível |
| Trace completo até React | 🟡 código e teste integrado; faltou consulta real falada |
| Release Gate | **BLOQUEADO** |

Conclusão: o Workbench agora espelha o Runtime vivo no caminho que foi
alinhado, mas a plataforma ainda não pode declarar a Sprint concluída. O
comportamento observado continua divergindo do ADR de streaming incremental no
provider de Speech ativo e ainda existe um caminho batch paralelo.
