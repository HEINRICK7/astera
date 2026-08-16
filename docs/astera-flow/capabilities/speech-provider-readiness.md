# Speech Provider Readiness Checklist

## Decisão

**Development Provider: faster-whisper APPROVED. Benchmark Provider: Parakeet
adapter IMPLEMENTED; execução real ainda NOT READY neste ambiente.**

O caminho de desenvolvimento usa faster-whisper em CPU. O caminho de benchmark
usa o contrato atual e integra batch via REST e streaming via WebSocket do
NVIDIA ASR NIM. A validação de benchmark depende de NIM Parakeet disponível,
GPU/ambiente suportado e áudio autorizado.

## Checklist

| Pergunta | Estado | Evidência |
|---|---|---|
| `SpeechTranscriber` cobre batch? | ✅ Sim | `transcribe(AudioRequest) → Transcript` |
| O contrato cobre streaming? | ✅ Boundary | `SpeechStreamingTranscriber` e `SpeechPlugin.invoke_stream` preservam chunks ordenados |
| Timestamps existem? | ✅ Sim | `TranscriptSegment` suporta segmento e `SpeechWord` suporta word-level |
| Confidence existe? | ✅ Parcial | confidence opcional por segmento; alguns modelos podem não fornecer word confidence |
| Speaker identification existe? | ✅ Parcial | `speaker` opcional por segmento; diarização é responsabilidade do provider |
| Metadados provider/language existem? | ✅ Sim | `Transcript.provider`, `language`, request id e metadata |
| Erros do provider são normalizados? | ✅ Boundary | `SpeechPlugin` converte falhas externas para `SpeechProviderError` sem expor payload bruto |
| Provider determinístico pode ser substituído no batch? | ✅ Sim | boundary `SpeechTranscriber` isolada |
| Development Provider roda sem GPU? | ✅ Sim | faster-whisper CPU/int8; instalação em `requirements-dev.txt` |
| Provider real pode ser substituído sem alterar o restante? | 🟢 Adapter pronto / runtime pendente | `ParakeetNimTranscriber` implementa os ports sem alterar Kernel ou consumidores |

## Escopo de hardening

Estado do hardening provider-neutral:

1. ✅ confidence ausente representada como `None`;
2. ✅ áudio inválido normalizado como `INVALID_AUDIO`; `RATE_LIMITED` está
   disponível para adapters que reconheçam esse estado;
3. ✅ `AudioRequest.request_id` é estável e deriva de `audio_id`, permitindo
   repetir a mesma requisição sem trocar a chave de idempotência;
4. ✅ adapter Parakeet NIM implementado; execução e benchmark pendentes;
5. 🟡 CQA, Medical Validation e Certification.

O retry do adapter cobre falhas transitórias do NIM; o retry executor permanece
responsabilidade operacional do chamador. O contrato garante que uma nova
tentativa receba o mesmo `request_id`. Isso é evolução da Capability Speech, não
mudança na Platform ou no Kernel.

## Evidência de ambiente

- `faster-whisper` 1.2.1 instalado e executado em ambiente temporário, sem
  alterar o repositório;
- modelo `tiny` carregado em CPU/int8 e chamado pelo adapter provider-neutral;
- smoke com 1 segundo de silêncio sintético: runtime executou, mas não houve
  fala e o adapter retornou `TRANSCRIPTION_FAILED` por ausência de segmentos;
- NIM Parakeet local: não encontrado;
- GPU NVIDIA utilizável: não disponível nesta sessão;
- `NGC_API_KEY`: ausente;
- áudio clínico autorizado: não disponível;
- transcript de áudio falado: não executado;
- benchmark real: não executado.

## Referências do provider

- [faster-whisper — official repository](https://github.com/SYSTRAN/faster-whisper)
- [NVIDIA ASR NIM](https://docs.nvidia.com/nim/speech/latest/asr/index.html)
- [NVIDIA NeMo ASR models](https://github.com/NVIDIA-NeMo/NeMo/blob/main/docs/source/asr/models.rst)
- [NVIDIA NeMo Speech inference](https://docs.nvidia.com/nemo/speech/nightly/asr/inference.html)
- [NVIDIA ASR HTTP REST API](https://docs.nvidia.com/nim/speech/latest/reference/api-references/asr/http-asr.html)
- [NVIDIA ASR Realtime WebSocket API](https://docs.nvidia.com/nim/speech/latest/reference/api-references/asr/realtime-asr.html)
