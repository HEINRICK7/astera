# Astera Research

Centro isolado de pesquisa para estudar, executar e medir providers reais,
benchmarks, datasets e experimentos antes de qualquer integração com o Astera.

O **Provider Lab** é o primeiro módulo ativo deste centro de pesquisa.

## Era 4 — Provider Research & Integration

O projeto principal permanece congelado. Este laboratório responde, para cada
provider, quatro perguntas:

1. Como o runtime funciona?
2. Quais capacidades e limitações foram comprovadas?
3. Que evidências de desempenho e confiabilidade existem?
4. Como o comportamento mapeia para os contratos já existentes?

Somente depois dessas respostas o provider pode ser considerado candidato a
integração no Astera.

## Isolamento obrigatório

- Este diretório não importa módulos de `apps/` ou `packages/`.
- Nenhum contrato, SDK, plugin, Kernel ou modelo cognitivo do Astera é
  alterado pelo laboratório.
- Credenciais, áudio autorizado, transcripts esperados e resultados brutos
  permanecem fora do Git.
- Falha de infraestrutura é registrada como falha de infraestrutura; não há
  fallback determinístico silencioso.
- O primeiro provider da Era 4 é exclusivamente o NVIDIA Parakeet. Outros
  providers só entram após a retrospectiva do primeiro ciclo.

## Laboratórios

| Capability | Development Provider | Benchmark Provider | Estado |
| --- | --- | --- | --- |
| Speech Transcription | faster-whisper | NVIDIA Parakeet NIM | Dev aprovado · benchmark pendente |

Consulte [Provider Lab / Parakeet](providers/speech/parakeet/README.md) para o
primeiro experimento.

## Governança executiva

- [Technology Readiness Level](technology-readiness-level.md)
- [Provider Maturity Dashboard](provider-maturity-dashboard.md)
- [Decision Log](decision-log.md)
- [Provider Scorecard](provider-scorecard.md)
