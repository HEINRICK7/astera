# Speech Transcription — Certification Session 001

| Campo | Valor |
|---|---|
| **Session** | `speech-transcription-certification-001` |
| **Capability** | `speech.transcription` |
| **Version** | `1.0.0` |
| **Status** | In Progress |
| **Certification** | Not Issued |
| **Production Ready** | No |
| **Started** | 2026-08-07 |
| **Evidence source** | Astera repository + Astera Flow |

## Escopo

Validar a capability Speech Transcription como produto, não apenas como plugin.
Esta sessão não executa Medical Validation ou CQA por inferência; esses gates
precisam de casos, baseline e revisão próprios.

## Gate matrix

| Gate | Status | Evidência | Observação |
|---|---|---|---|
| Engineering | PASS | `apps/runtime/tests/test_speech_plugin.py` | lifecycle, capability, health e transcrição determinística |
| Medical Validation | NOT RUN | — | nenhum verdict clínico emitido |
| CQA | NOT RUN | — | nenhum caso avaliado nesta capability |
| Regression | NOT RUN | — | baseline de capability ainda não aprovado |
| Performance | NOT RUN | — | benchmark de provider real ainda não executado |
| Security | NOT RUN | — | assessment específico ainda não executado |
| Observability | NOT RUN | — | evidência operacional de produção ainda não emitida |
| Documentation | PASS | `speech-transcription.md` | contrato, boundary e critérios documentados |

## Engineering evidence

- `AudioRequest` valida identidade, áudio, MIME type e sample rate.
- `SpeechTranscriber` é um port provider-neutral.
- `SpeechPlugin` registra `speech.transcription` e
  `speech.language_detection`.
- Provider health e resolver lifecycle são cobertos por teste.
- `Transcript` preserva request id, idioma, provider e segmentos.

## Próximas evidências

1. Registrar providers reais aprovados e seus artefatos de versão.
2. Executar benchmark de transcrição com dataset autorizado.
3. Usar a [CQA Case Selection 001](speech-transcription-cqa-selection-001.md)
   para enviar casos aplicáveis ao Cognitive Validation Lab.
4. Obter Medical Validation e CQA verdicts.
5. Criar baseline de regressão e executar performance/security/observability.
6. Submeter o Certification Record ao Astera Flow.

## Decisão atual

`Engineering Complete` é aceito. `Certified` e `Production Ready` permanecem
sem emissão até que todos os gates obrigatórios estejam em `PASS`.
