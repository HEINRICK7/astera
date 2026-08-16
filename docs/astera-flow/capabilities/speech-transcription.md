# Capability Zero — Speech Transcription

| Campo | Valor |
|---|---|
| **Capability** | `speech.transcription` |
| **Status atual** | Engineering Complete · Deterministic Provider · Real Provider Pending |
| **Certification** | Not Issued |
| **Production Ready** | No |
| **Providers de contrato** | Provider-neutral; Parakeet/Whisper reais ainda não integrados |
| **Plugin** | `speech-plugin` |

## Contrato

```text
AudioRequest → SpeechTranscriber → Transcript → Runtime
```

O transcript preserva request id, provider, idioma, segmentos, timestamps,
speaker e confidence quando fornecidos.

## Gates atuais

| Gate | Status | Evidência |
|---|---|---|
| Engineering | PASS | Speech SDK, Plugin SDK, lifecycle e testes determinísticos |
| Medical Validation | NOT RUN | nenhum verdict clínico emitido |
| CQA | NOT RUN | casos ainda não avaliados como capability |
| Regression | NOT RUN | baseline de capability ainda não criado |
| Performance | NOT RUN | benchmark de produção não executado |
| Security | NOT RUN | assessment específico da capability não executado |
| Observability | NOT RUN | certificação operacional não emitida |
| Documentation | PASS | contrato, plugin e Construction documentados |
| Certification | NOT ISSUED | gates obrigatórios incompletos |

## Critério de promoção

Speech Transcription só poderá receber `Production Ready` após todos os gates
acima terem evidência versionada e revisão no Astera Flow.

## Próximo trabalho

Executar o [Speech Benchmark 001](sessions/speech-transcription-benchmark-001.md)
com providers reais aprovados, executar
Medical Validation/CQA e registrar uma Regression Suite específica. Isso não
altera o contrato `SpeechTranscriber` nem o Kernel.

Sessão aberta: [Speech Transcription Certification 001](sessions/speech-transcription-certification-001.md).

Readiness do provider real: [Speech Provider Readiness Checklist](speech-provider-readiness.md).
