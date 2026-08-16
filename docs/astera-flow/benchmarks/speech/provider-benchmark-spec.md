# Speech Provider Benchmark Specification

## Contract under test

`SpeechTranscriber.transcribe(AudioRequest) → Transcript`  
O boundary também expõe `ProviderTrace`, métricas e diagnósticos como evidência
aditiva, sem alterar o output clínico consumido pelos pipelines.

## Same input

- MIME type, sample rate, language and audio bytes equivalentes;
- mesma referência autorizada;
- mesmo hardware profile e limites de concorrência;
- mesma versão do benchmark harness.

## Measurements

| Dimension | Measurement |
|---|---|
| Accuracy | WER/CER e medical-term fidelity |
| Latency | p50/p95 end-to-end e time-to-first-result |
| Streaming | chunk ordering, partial/final semantics e recovery |
| Metadata | timestamps, confidence, language e speaker preservation |
| Resource | CPU, GPU, memory, throughput e RTFX |
| Reliability | timeout, retry-safe behavior, provider error rate |
| Language | pt-BR coverage and punctuation |

## Acceptance

O provider só pode ser recomendado para a Capability quando os resultados,
limitações, licença e ambiente forem registrados. Recomendação de provider não
emite `Capability Certified` automaticamente.
