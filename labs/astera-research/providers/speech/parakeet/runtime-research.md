# Runtime Research Report — NVIDIA Parakeet Speech NIM

Status: Research complete from official documentation; local runtime not
executed.

Data da pesquisa: 2026-08-07  
Escopo: NVIDIA Speech NIM ASR, com foco em Parakeet e APIs batch/realtime.

## 1. Arquitetura do runtime

O Speech NIM é distribuído como container NVIDIA para servir modelos de fala
com runtime otimizado. O deployment self-hosted usa Docker, imagem disponível
no NGC e seleção de perfil por `NIM_TAGS_SELECTOR`.

Interfaces documentadas:

- HTTP REST para transcrição offline/batch, normalmente na porta `9000`.
- gRPC para streaming e respostas mais ricas.
- WebSocket realtime em `/v1/realtime?intent=transcription`, na porta `9000`.
- gRPC exposto normalmente na porta `50051`.

O laboratório usa HTTP e WebSocket para a primeira caracterização. O gRPC
fica explicitamente registrado como experimento posterior, não como uma
capacidade assumida.

## 2. Deployment e dependências

Requisitos documentados incluem Linux x86_64, Docker com NVIDIA Container
Toolkit, driver NVIDIA compatível, GPU com capacidade computacional suportada,
memória conforme o modelo/perfil, acesso ao NGC e licenciamento aplicável,
incluindo NVIDIA AI Enterprise para self-hosting quando exigido.

O compose deste Lab exige `NGC_API_KEY` e `runtime: nvidia`. Ele não deve ser
executado em modo CPU nem trocar a imagem por um servidor local diferente.

## 3. Batch HTTP

Endpoint:

```text
POST /v1/audio/transcriptions
Content-Type: multipart/form-data
```

O request inclui o arquivo de áudio e parâmetros como `language` e `model`
quando aplicáveis. A API documenta WAV, OPUS e FLAC para este caminho.

Resposta mínima documentada:

```json
{"text":"..."}
```

Conclusão de pesquisa: batch é adequado para medir transcrição offline, mas
não deve ser tratado como fonte de timestamps, confidence ou eventos parciais
sem evidência adicional do runtime.

## 4. Realtime WebSocket

Antes da conexão, o cliente pode criar uma sessão em:

```text
POST /v1/realtime/transcription_sessions
```

A sessão documenta `input_audio_format: pcm16`, sample rate padrão de 16000 Hz,
um canal e configuração de reconhecimento. A conexão usa:

```text
ws://<host>:9000/v1/realtime?intent=transcription
```

O cliente deve enviar:

1. `transcription_session.update`;
2. um ou mais `input_audio_buffer.append` com áudio Base64;
3. `input_audio_buffer.commit`;
4. `input_audio_buffer.done` para processamento de arquivo.

O tamanho máximo documentado para uma mensagem de áudio é 15 MB; o servidor
também documenta limite de mensagem de 10 MB, portanto o Lab deve medir o
limite efetivo do container selecionado e manter chunks pequenos.

Eventos de saída documentados:

- `conversation.item.input_audio_transcription.delta` com transcrição parcial;
- `conversation.item.input_audio_transcription.completed`;
- `conversation.item.input_audio_transcription.failed`;
- `error`;
- eventos de sessão e buffer.

## 5. Payload rico documentado

O evento `completed` pode conter:

```json
{
  "transcript": "...",
  "words_info": {
    "words": [
      {
        "word": "Hello",
        "start_time": 0.0,
        "end_time": 1.0,
        "confidence": 0.95,
        "speaker_tag": 0
      }
    ]
  },
  "vad_states": {
    "vad_states": [
      {"timestamp": 0.0, "prob": 0.5}
    ]
  },
  "is_last_result": false
}
```

Esses campos são documentação de contrato do provider, não evidência de que
o modelo/perfil escolhido os emitirá. O `realtime_probe.py` captura o evento
bruto para verificar isso.

## 6. VAD, diarização e vocabulário

### VAD

Há `vad_states` na resposta e configuração de endpointing na sessão. O Lab
deve medir presença, resolução e utilidade desses estados; não vai convertê-los
automaticamente em fatos clínicos.

### Speaker diarization

A sessão possui `speaker_diarization.enable_speaker_diarization` e
`max_speaker_count`; os words podem conter `speaker_tag`. A disponibilidade
efetiva deve ser verificada no perfil e modelo selecionados.

### Hotwords

O nome oficial documentado é `word_boosting`, com `word_boosting_list`. Isso é
um mecanismo de boosting de palavras, não prova a existência de vocabulário
médico nem de adaptação clínica.

### Vocabulário médico

Não foi encontrada, na API pesquisada, uma garantia de vocabulário médico
embutido. A hipótese só poderá ser avaliada com dataset clínico autorizado e
comparação de termos; permanece **não comprovada**.

## 7. Recovery e limitações

O provider documenta códigos WebSocket 1000, 1008, 1011 e 1013, além de
timeouts de inatividade e limites de conexão/mensagem. A documentação orienta
que o cliente implemente tratamento de erro e reconexão.

O Lab mede reconexão em experimento separado. Uma reconexão não será considerada
transparente se houver perda de chunk, duplicação de delta ou mudança de
transcript sem evidência.

## 8. Mapeamento candidato, sem alteração de contrato

O mapeamento só será implementado depois do Lab:

| Provider | Destino candidato | Condição |
| --- | --- | --- |
| batch `text` | texto de transcript | resposta HTTP comprovada |
| realtime `transcript` | texto final | evento completed comprovado |
| `delta` | resultado parcial | sem promover parcial a final |
| `words_info` | palavras, tempos e confidence | campos presentes no contrato existente |
| `speaker_tag` | metadado de fala | suporte comprovado no contrato existente |
| `vad_states` | diagnóstico técnico | não vazar para domínio clínico |

Nenhuma lacuna será resolvida criando entidade, SDK, contrato ou fallback no
Astera. Se o contrato existente não representar um campo provider-specific,
esse campo permanecerá diagnóstico do Lab até uma decisão arquitetural baseada
em evidência.

## Fontes oficiais

- [NVIDIA Speech NIM — ASR overview](https://docs.nvidia.com/nim/speech/latest/asr/index.html)
- [Parakeet CTC deployment](https://docs.nvidia.com/nim/speech/latest/asr/deploy-asr-models/parakeet-ctc-en-us.html)
- [HTTP ASR API](https://docs.nvidia.com/nim/speech/latest/reference/api-references/asr/http-asr.html)
- [Realtime WebSocket API](https://docs.nvidia.com/nim/speech/latest/reference/api-references/asr/realtime-asr.html)
- [ASR support matrix](https://docs.nvidia.com/nim/speech/latest/reference/support-matrix/asr.html)
- [Speech NIM prerequisites](https://docs.nvidia.com/nim/speech/latest/get-started/prerequisites.html)
