# Provider Maturity Dashboard

Atualizado em 2026-08-07. Este dashboard é executivo e evidencia o estado do
Research; não deve ser confundido com número de testes do Astera Core.

## Visão atual

| Área | Estado | Evidência |
| --- | --- | --- |
| Astera Core | Stable | arquitetura congelada e contratos existentes |
| Cognitive Model | Stable | especificação e validações conceituais existentes |
| Capability Platform | Stable | capability/provider boundary existente |
| Provider Ecosystem | Directional 30% | processo definido; poucos providers pesquisados |
| Astera Research | Directional 10% | centro criado; primeiro Lab em preparação |
| Clinical Production | 0% | nenhuma Clinical Workflow Certification |

## Providers

| Capability | Development Provider | Benchmark Provider | TRL | Documentado | Comprovado | Benchmark | Medical | Certificação | Produção |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| Speech | faster-whisper ✅ | NVIDIA Parakeet NIM | 2 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Vision | PaddleOCR/CPU baseline pending | Qwen2.5-VL | 0 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Terminology | Snowstorm ✅ | Pending | 0 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Embeddings | multilingual-e5-small ✅ | BGE-M3 | 0 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## Leitura executiva

Parakeet está no nível **Lab criado**, não no nível Runtime Validado. O
faster-whisper é o Development Provider oficial de Speech e não depende do
runtime Parakeet. O quadro não afirma desempenho, qualidade médica, licença
operacional ou prontidão de produção enquanto os respectivos experimentos não
existirem.
