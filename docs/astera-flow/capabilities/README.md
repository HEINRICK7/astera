# Capability Roadmap

| Campo | Valor |
|---|---|
| **Status** | Active |
| **Strategy** | Capability-first |
| **Architecture** | Capability → Provider → Plugin |
| **Certification authority** | Astera Flow + Cognitive Validation Lab |
| **Production certification** | Not yet issued |

## Five-question rule

Toda Capability deve responder apenas [estas cinco perguntas](capability-definition-template.md).
Certification, benchmarks e CQA são evidências de validação, não novas camadas
conceituais do produto.

## Nova unidade de entrega

Depois da fundação e da Construction, o Astera deixa de organizar a evolução
por fases técnicas e passa a organizar o produto por capacidades que podem ser
descobertas, avaliadas e certificadas:

```text
Capability → Engineering → Medical Validation → CQA
           → Regression → Certification → Production
```

O produto expõe capacidades. Providers e Plugins são meios substituíveis de
entregá-las.

## Capability lifecycle

```text
Identified
   ↓
Engineering Complete
   ↓
Medical Validation
   ↓
CQA
   ↓
Regression
   ↓
Certified
   ↓
Production Ready
```

`Engineering Complete` não equivale a `Production Ready`. Cada gate precisa de
evidência própria no Astera Flow.

## Capability Zero

O primeiro objetivo comercial é certificar `Speech Transcription` como uma
capacidade independente e, em seguida, certificar a composição `Clinical
Consultation Core`:

```text
Speech Transcription
        ↓
Clinical Facts Extraction
        ↓
Clinical Context
        ↓
Clinical Reasoning
        ↓
Medical Knowledge
        ↓
Clinical Documentation
        ↓
Persistence
```

O código atual comprova Engineering Complete para o slice determinístico. A
certificação Production Ready ainda não foi emitida porque os gates clínicos,
CQA, performance, segurança específica e operação precisam ser executados.

## Regras

1. O roadmap não cria novos conceitos cognitivos nem altera o Kernel.
2. Uma capability só pode ser chamada `Production Ready` com certification
   record aprovado.
3. Teste de software e CQA continuam pipelines independentes.
4. Uma falha de capability corrige implementação quando o contrato permanece
   válido; mudança arquitetural segue a ADR-010.
5. O trabalho dos agentes é promover capabilities, não criar documentação ou
   abstração sem necessidade.

## Documentos

- [Capability status board](capability-roadmap.md)
- [Capability cards](capability-cards.md)
- [Certification contract](capability-certification.md)
- [Speech Transcription](speech-transcription.md)
- [Speech Provider Readiness](speech-provider-readiness.md)
- [Speech Certification Session 001](sessions/speech-transcription-certification-001.md)
- [Speech Benchmark 001](sessions/speech-transcription-benchmark-001.md)
- [Speech CQA Case Selection 001](sessions/speech-transcription-cqa-selection-001.md)
- [Cognitive Validation Lab](../cognitive-validation-lab/README.md)
- [Architecture Freeze](../../adrs/ADR-010-architecture-freeze.md)
