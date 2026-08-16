# Construction Sprint 1 — Speech Plugin

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Módulo** | Speech Plugin |
| **Capability** | `speech.transcription`, `speech.language_detection` |
| **Decisão** | Implementação existente validada; nenhuma duplicação necessária |

## Resultado

O Speech Plugin já implementa a boundary aprovada usando o Plugin SDK:

```text
AudioRequest → SpeechTranscriber → Transcript → Runtime
```

O provider permanece substituível e o plugin registra capability, provider,
health e lifecycle no Runtime.

## Validação registrada

- Registro e remoção do provider no lifecycle.
- Transcrição determinística para contract tests.
- Preservação de idioma, segmentos e confidence.
- Provider healthy após `on_start`.
- Integração no pipeline de consulta existente.

## Arquivos de referência

- `packages/speech_sdk/models.py`
- `packages/speech_sdk/protocol.py`
- `packages/speech_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/speech/plugin.py`
- `apps/runtime/tests/test_speech_plugin.py`

## Próximo módulo

**Clinical Facts Plugin — In Progress**. O plugin consumirá sinais estruturados
do Medical NLP e preservará provenance, polaridade, certainty, subject e
encounter conforme o contrato de Clinical Fact.
