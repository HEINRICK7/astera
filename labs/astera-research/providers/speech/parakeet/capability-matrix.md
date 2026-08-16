# Provider Capability Matrix — NVIDIA Parakeet NIM

Atualizada em 2026-08-07. A coluna **Documentação** registra o que a API
oficial descreve. A coluna **Runtime** só pode ser marcada depois de executar
o probe contra o NIM selecionado.

| Recurso | Documentação | Runtime | Evidência exigida | Observação |
| --- | --- | --- | --- | --- |
| Batch transcription | ✅ | ⬜ | resposta HTTP bruta | `POST /v1/audio/transcriptions`; resposta mínima contém `text` |
| Streaming | ✅ | ⬜ | JSONL realtime | WebSocket com `intent=transcription` |
| Partial results | ✅ | ⬜ | eventos `delta` | Não assumir estabilidade sem medir os deltas |
| Word timestamps | ✅ realtime | ⬜ | `words_info.words[]` | Não documentado como retorno do batch HTTP |
| Word confidence | ✅ realtime | ⬜ | `confidence` por palavra | Não confundir com confiança clínica |
| Speaker diarization | ✅ configuração | ⬜ | `speaker_tag` com sessão habilitada | Disponibilidade efetiva depende do runtime/modelo |
| VAD | ✅ output/configuração | ⬜ | `vad_states` e endpointing | Medir qualidade separadamente da transcrição |
| Hotwords | ✅ como `word_boosting` | ⬜ | sessão com lista controlada | O nome oficial é word boosting |
| Vocabulário médico | ❓ | ⬜ | benchmark clínico autorizado | Não comprovado pela existência de word boosting |
| Language detection | ❓ dependente do modelo | ⬜ | `/v1/models` + experimento | Não inferir suporte pt-BR para este container |
| WAV/OPUS/FLAC batch | ✅ | ⬜ | três probes | Formatos aceitos pelo endpoint HTTP |
| PCM16 mono realtime | ✅ | ⬜ | probe PCM | Default documentado: 16 kHz, 1 canal |
| Reconnect/recovery | cliente deve implementar | ⬜ | teste de interrupção | O provider expõe códigos de fechamento; recuperação é responsabilidade do cliente |
| Latência/throughput | não é garantia | ⬜ | benchmark repetido | Registrar TTFT, tempo total, RTFx e throughput |
| CPU/GPU/memória | requisitos documentados | ⬜ | métricas do host/NIM | Medir por perfil e hardware, nunca extrapolar |

## Perguntas ainda abertas

1. O container e perfil escolhidos expõem exatamente todos os campos realtime
   descritos pela API?
2. O diarization e o VAD estão disponíveis no perfil Parakeet selecionado?
3. Qual é o comportamento de `word_boosting` em termos médicos e por idioma?
4. Quais são os limites práticos de chunk, conexão e concorrência neste
   hardware?
5. Qual a qualidade em pt-BR? Não será declarada sem modelo suportado e dataset
   autorizado.

## Critério de atualização

Cada célula `Runtime` precisa apontar para um resultado JSONL/JSON fora do Git,
com versão do container, modelo, perfil, hardware, dataset e timestamp. Uma
leitura da documentação nunca será registrada como execução bem-sucedida.
