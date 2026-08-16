# Provider Scorecard — NVIDIA Parakeet NIM

O scorecard não atribui notas sem medição. `Not measured` é um resultado
válido e diferente de zero.

| Dimensão | Estado atual | Evidência |
| --- | --- | --- |
| Documentation | ✅ Available | documentação oficial NVIDIA pesquisada |
| Deployment | ⬜ Blocked | GPU, driver, NGC e licença ainda não disponíveis |
| Batch | ⬜ Not measured | probe criado; NIM não executado |
| Streaming | ⬜ Not measured | probe WebSocket criado; NIM não executado |
| Partial results | ✅ Documented / ⬜ Runtime | eventos delta documentados |
| Word timestamps | ✅ Documented / ⬜ Runtime | `words_info.words[]` documentado no realtime |
| Confidence | ✅ Documented / ⬜ Runtime | confidence por palavra documentada |
| Speaker diarization | ✅ Config documented / ⬜ Runtime | `speaker_tag` depende do perfil/modelo |
| VAD | ✅ Output documented / ⬜ Runtime | `vad_states` depende da execução |
| Medical vocabulary | ❓ Unverified | word boosting não é prova clínica |
| Performance | ⬜ Not measured | requer hardware e dataset fixados |
| CPU/GPU/memory | ⬜ Not measured | requer coleta do host/NIM |
| Observability | ⬜ Not measured | endpoints disponíveis; métricas ainda não capturadas |
| License | ⬜ Verification pending | confirmar termos do ambiente de deployment |

## Regra de pontuação futura

Cada dimensão receberá nota somente após um artefato versionado contendo
`run_id`, versão da imagem, perfil, hardware, dataset, parâmetros e resultado.
Uma nota agregada só será exibida quando todas as dimensões obrigatórias do
gate estiverem medidas.
