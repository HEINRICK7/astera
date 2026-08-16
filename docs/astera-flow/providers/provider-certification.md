# Provider Certification

## Objetivo

Certificar um provider real sem alterar o contrato da Capability, do Plugin, do
Kernel ou dos consumidores downstream.

## Lifecycle

```text
Draft
  ↓
Implemented
  ↓
Engineering Approved
  ↓
Benchmarked
  ↓
Medical Validated
  ↓
CQA Approved
  ↓
Certified
  ↓
Production Ready
  ↓
Deprecated → Retired
```

## Gates obrigatórios

| Gate | Evidência mínima |
|---|---|
| Engineering | adapter implementado e contrato aprovado |
| Benchmark | mesmo Golden Dataset e resultados comparáveis |
| Stress Test | comportamento sob concorrência, timeout e recuperação |
| Medical Validation | fidelidade clínica avaliada |
| CQA | ausência de perda ou criação indevida de informação |
| Observability | `ProviderTrace`, métricas e diagnósticos disponíveis |
| Documentation | versão, ambiente, limitações e licença registradas |

Nenhum provider recebe `Certified` ou `Production Ready` com gate ausente,
mesmo que os testes de engenharia passem.

## Primeiro candidato

| Campo | Estado |
|---|---|
| Capability | Speech Transcription |
| Provider | NVIDIA Parakeet |
| Estado atual | Adapter Implemented · Runtime Pending |
| Adapter real | Implementado contra NVIDIA ASR NIM |
| Golden Dataset | Pendente |
| Medical Validation | Pendente |
| CQA | Pendente |
| Certification | Não emitida |
| Production | Não pronto |

## Provider Trace

Cada execução deve preservar, no mínimo:

```text
request_id
provider
provider_version
capability
plugin
kernel_version
started_at
finished_at
latency_ms
retries
status
error
confidence
streaming
```

O `request_id` é o vínculo entre a chamada do provider e as etapas posteriores
do Encounter. O retry executor pode repetir uma chamada, mas deve reutilizar o
mesmo identificador.

`ProviderTrace` pertence exclusivamente a Infrastructure/Observability e ao
Benchmark Lab. O Clinical Domain não deve receber esse objeto.

## ProviderExecutionResult

O boundary do provider expõe o resultado clínico acompanhado de:

- `trace` para auditoria;
- `metrics` para Benchmark Lab;
- `diagnostics` para investigação operacional.

O `Transcript` continua sendo o output clínico consumido pelos pipelines. O
envelope de evidências é obtido pelo caminho explícito `execute_with_evidence`
do Plugin e não é incluído no retorno clínico de `invoke`/`invoke_stream`.

## Regra de troca

Um provider novo só é aceito quando puder substituir o provider atual através do
mesmo `SpeechTranscriber` e do mesmo `SpeechPlugin`, sem alteração no Kernel ou
nas etapas de Clinical Facts, Context, Reasoning, Knowledge e Documentation.

O adapter atual usa o endpoint REST `/v1/audio/transcriptions` para batch e o
endpoint WebSocket `/v1/realtime?intent=transcription` para streaming. A
implementação não é evidência de execução, benchmark ou certificação.
