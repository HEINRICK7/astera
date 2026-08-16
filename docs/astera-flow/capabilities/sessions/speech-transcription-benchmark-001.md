# Speech Transcription — Benchmark 001

| Campo | Valor |
|---|---|
| **Session** | `speech-transcription-benchmark-001` |
| **Capability** | `speech.transcription` |
| **Status** | Ready |
| **Purpose** | Engineering benchmark before certification |
| **Production verdict** | Not issued |

## Objetivo

Medir a capacidade de transcrição como produto, comparando providers aprovados
com o mesmo corpus autorizado e o mesmo contrato `SpeechTranscriber`.

## Dimensões

| Métrica | Definição | Resultado |
|---|---|---|
| Latency p50/p95 | tempo de `AudioRequest` até `Transcript` | NOT RUN |
| Throughput | áudios processados por janela | NOT RUN |
| Transcript completeness | segmentos e timestamps preservados | NOT RUN |
| Provider error rate | falhas por request | NOT RUN |
| Language fidelity | idioma solicitado/preservado | NOT RUN |
| Resource profile | CPU, memória e GPU quando aplicável | NOT RUN |

## Regras

- O corpus precisa ter licença e autorização registradas.
- Providers devem usar a mesma unidade de comparação.
- Benchmark determinístico local é apenas smoke test, não resultado de produção.
- Métricas não certificam fidelidade clínica; CQA e Medical Validation continuam
  obrigatórios.
- Nenhum resultado será inventado a partir de fixtures in-memory.

## Entrada necessária

1. Provider(s) aprovados pelo Astera Flow.
2. Corpus autorizado e sua provenance.
3. SLOs de performance da capability.
4. Ambiente e perfil de hardware definidos.

## Saída

Um relatório versionado com raw measurements, ambiente, provider/version,
estatística, limitações e referência à Certification Session 001.
