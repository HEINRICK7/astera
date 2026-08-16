# Astera Benchmark Lab

Repositório lógico de benchmarks de Providers e Foundation Models. Os dois
benchmarks possuem boundaries e lifecycles separados; nenhum altera o contrato
nem o Kernel.

## Estrutura

```text
benchmarks/
├── speech/
├── vision/
├── ocr/
├── medical-nlp/
├── terminology/
├── fhir/
├── embeddings/
└── reasoning/
```

## Provider benchmark lifecycle

```text
Same Contract
    ↓
Provider A / Provider B / Provider C
    ↓
Quality + Latency + Cost + Resource + Security
    ↓
Medical/CQA Evidence
    ↓
Provider Certification
```

## Regras

- Todos os providers recebem exatamente o mesmo contrato e corpus autorizado.
- Raw clinical data não entra no repositório.
- Resultados carregam provider version, ambiente, dataset hash e timestamp.
- WER, latency, throughput ou score não equivalem automaticamente a
  certificação clínica.
- Um provider pode ser substituído sem alterar a Capability.

## Capabilities

- [Speech benchmark specification](speech/provider-benchmark-spec.md)
- [Provider evidence metrics](provider-evidence-metrics.md)
- [Capability cards](../capabilities/capability-cards.md)
- [Provider matrix](../providers/README.md)
- [Foundation Model benchmark](foundation-model-benchmark.md)
- [Foundation Model certification](foundation-model-certification.md)
- [Terminology provider benchmark](terminology-provider-benchmark.md)
- [Provider asset governance](PROVIDER_ASSET_GOVERNANCE.md)
