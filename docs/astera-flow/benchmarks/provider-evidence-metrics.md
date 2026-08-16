# Provider Evidence Metrics

## Objetivo

Medir a independência da Capability em relação ao Provider e comparar Providers
com evidências reproduzíveis. Esta página não altera contratos nem decide
certificação sozinha.

## Capability Independence Score

Mede quanto da plataforma foi alterado para integrar um Provider.

```text
100% − penalidades por alterações fora do adapter/provider boundary
```

Registro obrigatório:

| Campo | Valor |
|---|---|
| Provider | nome e versão |
| Provider files changed | lista do adapter |
| Kernel files changed | quantidade e lista |
| Contracts changed | quantidade e lista |
| Plugins changed | quantidade e lista |
| SDKs changed | quantidade e lista |
| Score | calculado após a integração |

Qualquer alteração no Kernel, nos contratos clínicos ou nos SDKs deve ser
explicitamente justificada e reduz o score.

## Provider Replaceability Index

Registra a troca entre dois Providers usando o mesmo contrato:

```text
minutes
files_changed
contracts_changed
kernel_changes
regression_failures
```

O índice só é considerado demonstrado quando a troca termina com a suíte de
regressão passando e sem mudança no Clinical Domain.

## Golden Clinical Dataset

Datasets são versionados e imutáveis por versão:

```text
Golden Clinical Dataset v1.0
  ├── Cardiology
  ├── Pediatrics
  ├── Psychiatry
  ├── Dermatology
  ├── Obstetrics
  ├── Orthopedics
  ├── Emergency
  └── Routine Care
```

Cada versão registra quantidade de casos, especialidade, hash, autorização,
proveniência e critérios de anonimização. A próxima versão gera uma nova rodada
de benchmark; resultados de versões anteriores não são sobrescritos.

O dataset clínico não fica armazenado neste repositório. Apenas manifests,
hashes e referências autorizadas podem ser versionados.

## Compatibility Matrix — Speech

| Provider | Streaming | Batch | pt-BR | CPU | GPU/SaaS | Estado |
|---|---:|---:|---:|---:|---:|---|
| DeterministicTranscriber | — | ✅ | ✅ | ✅ | — | Internal |
| NVIDIA Parakeet | Pendente | Pendente | Pendente | Pendente | Pendente | Candidate |
| Whisper | Pendente | Pendente | Pendente | Pendente | Pendente | Planned |
| Deepgram | Pendente | Pendente | Pendente | Pendente | SaaS | Planned |
| Azure Speech | Pendente | Pendente | Pendente | Pendente | SaaS | Planned |

`Pendente` significa ausência de evidência no Benchmark Lab, não uma conclusão
de incompatibilidade.

## Capability Health — estado atual

| Capability | Engineering | Coverage | Benchmark | Medical Validation | Certification | Production |
|---|---|---|---|---|---|---|
| Speech | PASS — 98 testes | Não medido | Pendente | Pendente | Não emitida | Não pronta |

Percentuais só devem ser publicados quando houver método de cálculo, dataset e
evidência versionados.
