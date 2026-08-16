# Parakeet Provider Integration Report

**Sprint:** 1 — NVIDIA Parakeet NIM Adapter  
**Data:** 2026-08-07  
**Status:** Adapter implementado · Runtime Integration bloqueado neste ambiente  
**Arquitetura:** sem alteração em Kernel, SDK, Plugin ou contratos públicos

## 1. Escopo investigado

O adapter foi analisado contra a documentação oficial do NVIDIA Speech NIM,
sem assumir que o modelo seria executado diretamente por Python/NeMo no processo
do Astera.

## 2. Runtime oficial

O NVIDIA ASR NIM é distribuído como container que empacota o modelo e a stack de
inferência NVIDIA. A implantação oficial usa Docker/NVIDIA Container Toolkit,
NGC e perfis selecionados por `NIM_TAGS_SELECTOR`.

| Aspecto | Evidência oficial |
|---|---|
| Runtime | NVIDIA Speech NIM container |
| Inference stack | TensorRT, Triton e componentes do NIM |
| Deployment | Docker ou Kubernetes/Helm, conforme ambiente |
| Batch | HTTP REST `POST /v1/audio/transcriptions` |
| Streaming | Realtime WebSocket `/v1/realtime?intent=transcription` |
| Streaming alternativo | gRPC, com API mais rica para output por palavra |
| Readiness | `GET /v1/health/ready` |
| Models | `/v1/models` e metadata do NIM |
| Metrics | `/v1/metrics` em formato Prometheus |

Fontes: [ASR NIM overview](https://docs.nvidia.com/nim/speech/latest/asr/index.html),
[HTTP API](https://docs.nvidia.com/nim/speech/latest/reference/api-references/asr/http-asr.html),
[Realtime API](https://docs.nvidia.com/nim/speech/latest/reference/api-references/asr/realtime-asr.html).

## 3. Batch

O endpoint REST recebe `multipart/form-data` com `file` e `language` ou
`model`. A documentação oficial lista WAV, OPUS e FLAC como formatos aceitos e
retorna JSON com `text`. O adapter envia exatamente esse formato e mapeia o
texto para o `Transcript` existente.

Limitação explícita: a resposta HTTP documentada não fornece word timestamps,
confidence ou speaker tags. O adapter não inventa esses valores; o batch gera
um segmento sem timestamps (`0..0`) e confidence ausente.

## 4. Streaming

O Realtime API usa WebSocket, sessão de transcrição, eventos de append/commit/done
e eventos de delta/completed/failed. O contrato realtime documentado exige
PCM16; o adapter rejeita WAV/OPUS/FLAC no método de streaming em vez de fazer
conversão silenciosa.

O adapter mapeia:

| NIM event | Speech contract |
|---|---|
| `...transcription.delta` | `TranscriptSegment(is_final=False)` |
| `...transcription.completed` | `TranscriptSegment(is_final=True)` |
| `words_info.words` | `SpeechWord` |
| `...transcription.failed` / `error` | `SpeechProviderError` |

## 5. Áudio e sample rate

| Caminho | Formato | Sample rate |
|---|---|---|
| Batch REST | WAV, OPUS, FLAC | preservado pelo arquivo/provider |
| Realtime WebSocket | PCM16 | sessão default 16 kHz; request pode informar sample rate |

O adapter não reamostra áudio. A normalização de sample rate deve ocorrer antes
do boundary do provider, quando exigida pelo dataset ou pelo perfil do NIM.

## 6. Hardware, CPU e dependências

A matriz oficial do ASR NIM exige GPU NVIDIA com Compute Capability 8.0 ou
superior e pelo menos 16 GB de VRAM, além de requisitos específicos por modelo.
O ambiente oficial também exige Linux/x86_64, NVIDIA Container Toolkit e driver
compatível. O tutorial oficial usa `NGC_API_KEY` para obter a imagem/modelo.

Não há um SLA oficial de latência no contrato do provider. Latência, throughput,
CPU, GPU e memória devem ser medidos no Benchmark Lab.

Fonte: [ASR support matrix](https://docs.nvidia.com/nim/speech/latest/reference/support-matrix/asr.html)
e [NIM prerequisites](https://docs.nvidia.com/nim/speech/latest/get-started/prerequisites.html).

Dependências client-side do adapter:

- `httpx` para REST batch;
- `websockets` para Realtime streaming.

O modelo e a stack de inferência permanecem no runtime NIM, não nas dependências
do Astera.

## 7. Licenciamento

A documentação de pré-requisitos informa que self-hosting de Speech NIM exige
licença NVIDIA AI Enterprise. A licença aplicável ao deployment do Astera deve
ser validada antes da certificação e registrada junto à evidência do provider.

Fonte: [NVIDIA Speech NIM prerequisites](https://docs.nvidia.com/nim/speech/latest/get-started/prerequisites.html).

## 8. Mapeamento para o Astera

| Astera | NVIDIA NIM |
|---|---|
| `SpeechTranscriber.transcribe` | HTTP batch transcription |
| `SpeechStreamingTranscriber.transcribe_stream` | Realtime WebSocket |
| `AudioRequest.audio` | multipart file ou base64 PCM16 |
| `AudioRequest.language` | NIM `language` |
| `AudioRequest.request_id` | identidade da tentativa no Astera |
| `Transcript.text` | NIM `text`/`transcript` |
| `TranscriptSegment` | delta/completed segment |
| `SpeechWord` | Realtime `words_info.words` |
| `SpeechProviderError` | status HTTP/WebSocket normalizado |

## 9. Decisões

1. O primeiro adapter usa NVIDIA ASR NIM, não importação direta de NeMo/PyTorch.
2. Batch e streaming usam endpoints oficiais distintos.
3. O adapter não converte formatos nem mascara ausência de metadados.
4. O `SpeechTranscriber` permanece inalterado.
5. O bootstrap injeta o adapter real; o determinístico permanece apenas em
   fixtures/testes.
6. Retry de streaming só reconecta antes do primeiro partial; depois que um
   partial foi emitido, a chamada falha sem duplicar segmentos já entregues.

## 10. Riscos e limitações

- O workspace não possui GPU funcional, NIM Parakeet, `NGC_API_KEY` ou áudio
  clínico autorizado.
- A seleção de perfil/modelo para pt-BR precisa ser confirmada no `/v1/models` e
  no benchmark; não é presumida pelo adapter.
- Batch REST não fornece os mesmos metadados do Realtime/gRPC.
- Latência e throughput ainda não têm evidência executada.
- A licença NVAIE e os termos do deployment ainda não foram validados para o
  ambiente de produção.

## 11. Estado da integração

| Gate | Estado |
|---|---|
| Adapter code | PASS |
| Contract compatibility | PASS |
| Batch transport tests | PASS |
| Streaming transport tests | PASS |
| Runtime integration | BLOCKED — NIM/GPU/credencial ausentes |
| Benchmark | PENDING |
| Medical Validation | PENDING |
| CQA | PENDING |
| Certification | PENDING |
