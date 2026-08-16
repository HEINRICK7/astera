# ASTERA-SPR-001 — Speech Runtime Consolidation

**Status:** In progress  
**Prioridade:** Crítica  
**Implementação registrada em:** 11/08/2026

## Escopo aplicado

- `SpeechEventType` agora expõe somente os eventos oficiais:
  `speech.started`, `speech.audio`, `transcript.created`,
  `transcript.partial`, `transcript.done`, `speech.stopped` e `speech.error`.
- Revisões continuam sendo atualizações do mesmo `segment_id` dentro de
  `transcript.partial`; não existe evento de revisão separado no wire contract.
- `StreamingTranscriptState` continua como estado único de segmentos, partial,
  transcript final, versão e lifecycle.
- Segmentos finalizados são imutáveis; eventos posteriores com o mesmo ID são
  descartados.
- Adicionados `trace_id`, `captured_at`, `received_at`, `processed_at` e
  `published_at` ao envelope de todos os eventos Speech.
- Adicionadas métricas canônicas de Speech: áudio, segmentos, revisões,
  latências, frames descartados, reconexões e erros.
- O áudio é observado pelo adapter como `speech.audio`; o antigo evento
  `speech.audio.received` deixou de ser publicado.
- Métricas clínicas de hipótese, SOAP e objetos clínicos foram retiradas do
  `StreamingTranscriptState` e permanecem no pipeline Clinical.
- O perfil padrão continua resolvendo para o adapter xAI STT.

## Arquivos principais

| Área | Arquivo |
|---|---|
| Contrato e estado | `packages/speech_sdk/models.py` |
| Adapter de sessão | `packages/speech_sdk/engine.py` |
| Provider xAI | `packages/speech_sdk/providers/xai.py` |
| Integração do pipeline | `apps/runtime/src/application/clinical/live_stream.py` |
| Transporte WebSocket | `apps/runtime/src/adapters/http/streaming.py` |
| Testes do contrato | `apps/runtime/tests/test_speech_sdk_contract.py` |

## Evidência executada

```text
137 passed, 4 warnings in 9.85s
```

Também foram atualizados os testes de adapter para verificarem a sequência
oficial, o evento de áudio, o trace ID e os timestamps.

## Pendências para marcar a Sprint como Done

- [ ] Conectar reconexão real do provider a `reconnects`.
- [ ] Contabilizar `dropped_frames` no ponto de ingestão quando houver backpressure.
- [ ] Cobrir timeout, cancelamento, provider indisponível e reconexão com testes
  de integração do WebSocket.
- [ ] Executar uma sessão real de 30 minutos e guardar evidência de memória,
  latência e ausência de duplicação.
- [ ] Isolar completamente o caminho batch legado do caminho de sessão contínua;
  o Faster Whisper permanece apenas como fallback de desenvolvimento.

Até essas evidências existirem, o status correto é **In progress**, não
**Done**.
