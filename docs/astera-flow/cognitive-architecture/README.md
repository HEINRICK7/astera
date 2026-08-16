# Cognitive Architecture

Domínio normativo da arquitetura cognitiva do Astera Flow.

```text
Cognitive Architecture
├── 01 - Clinical Facts
├── 02 - Clinical Context
├── 03 - Clinical Reasoning Loop
├── 04 - Medical Knowledge Layer
├── 05 - Specialists Architecture
├── 06 - Cognitive Contracts
├── 07 - Cognitive Events
├── 08 - Validation Scenarios
├── 09 - ADRs
├── 10 - Architecture Review
├── 11 - Clinical Simulation
├── 12 - Reality Review
└── 13 - Reality Case Registry
```

## Autoridade

Este domínio transforma os cinco workshops da Fase C.5 em uma especificação
formal. A RFC e seus documentos foram aprovados pelo Astera Flow como baseline
da versão 1.0. O código não é fonte de verdade para conceitos cognitivos; ele
implementa os contratos aprovados sob a ADR-010.

## Ciclo normativo

```text
Workshop
   ↓
RFC / Specification
   ↓
Architecture Review
   ↓
Engineering Review
   ↓
Reality Review
   ↓
Medical Validation
   ↓
ADR
   ↓
Astera Flow
   ↓
Implementation
```

Nenhum conceito cognitivo novo deve ser implementado fora desse ciclo.

## Documentos

1. [Clinical Facts](01-clinical-facts.md)
2. [Clinical Context](02-clinical-context.md)
3. [Clinical Reasoning Loop](03-clinical-reasoning-loop.md)
4. [Medical Knowledge Layer](04-medical-knowledge-layer.md)
5. [Specialists Architecture](05-specialists-architecture.md)
6. [Cognitive Contracts](06-cognitive-contracts.md)
7. [Cognitive Events](07-cognitive-events.md)
8. [Validation Scenarios](08-validation-scenarios.md)
9. [ADRs](09-adrs.md)
10. [Architecture Review](10-architecture-review.md)
11. [Clinical Simulation](11-clinical-simulation.md)
12. [Reality Review](12-reality-review.md)
13. [Cognitive Validation Lab](../cognitive-validation-lab/README.md)

Especificação principal: [RFC-001 — Astera Cognitive Architecture](RFC-001-astera-cognitive-architecture.md).

RFC proposta: [RFC-002 — Clinical Graph Architecture](RFC-002-clinical-graph.md).

Revisão de domínio: [Clinical Graph — Domain Review](clinical-graph-domain-review.md).

Revisão médica: [Clinical Consultation Graph — Medical Domain Review](clinical-graph-medical-domain-review.md).
