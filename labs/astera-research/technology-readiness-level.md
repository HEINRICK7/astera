# Technology Readiness Level — Astera Research

O Astera Research usa uma escala TRL inspirada na NASA, adaptada para
providers de software e modelos. Ela mede evidência acumulada; não é uma
certificação clínica e não substitui os gates do Astera Flow.

## Escala oficial do Research

| TRL | Nome | Evidência mínima |
| --- | --- | --- |
| 1 | Pesquisado | documentação, licença e limitações identificadas |
| 2 | Lab criado | experimento isolado, configuração reproduzível e probes |
| 3 | Runtime validado | runtime sobe e health/API respondem no ambiente alvo |
| 4 | Benchmark | métricas repetíveis em dataset versionado |
| 5 | Medical Validation | avaliação clínica autorizada e análise de falhas |
| 6 | Capability Certification | gates de engenharia, benchmark, CQA e validação aprovados |
| 7 | Clinical Workflow | participa de uma jornada clínica ponta a ponta certificada |
| 8 | Pilot | operação controlada com observabilidade, segurança e suporte |
| 9 | Production | aprovação operacional e clínica para produção |

## Regras

- Um provider não sobe de nível por intenção, código ou documentação de outro
  provider.
- Evidência ausente fica como `PENDING` ou `NOT MEASURED`, nunca como zero
  inventado ou aprovação implícita.
- TRL é atribuído ao provider/runtime específico, não apenas à capability.
- O Research pode recomendar avanço; o Astera Flow continua sendo a autoridade
  para aprovar a entrada no produto.

## Estado atual

| Provider | Capability | TRL | Motivo |
| --- | --- | ---: | --- |
| NVIDIA Parakeet NIM | Speech Transcription | 2 | Lab, Compose e probes criados; runtime ainda não executado |
| Qwen2.5-VL | Vision | 0 | Não iniciado |
| Snowstorm | Terminology | 0 | Não iniciado |
| BGE-M3 | Embeddings | 0 | Não iniciado |

