---
document_id: astera-flow-index
title: Astera Flow
category: Product
status: Official
version: 2.0
owner: Astera Product Engineering
depends_on:
  - ../AGENTS.md
  - ../adrs/ADR-011-platform-complete.md
used_by:
  - Todos os agentes do Astera
  - Product Engineering
last_updated: 2026-08-07
---

# Astera Flow

Este diretório concentra material relacionado ao fluxo operacional e à visão do sistema Astera Flow.

## Permanent fronts

```text
ASTERA
├── Clinical Product Increments
├── Platform
├── Capabilities
└── Providers
```

- [Product Backlog](product-backlog.md) — unidade oficial de entrega depois do
  encerramento arquitetural; organizado por CPIs.
- [PRD-001 — Patient Journey](PRD-001-patient-journey.md) — primeira jornada
  de produto do Astera Clinical; responde se o paciente consegue entrar.
- [Vision Demo](vision-demo.md) — filme de referência da primeira consulta
  completa do Astera Clinical.
- [Definition of Done](definition-of-done.md) — critérios obrigatórios para
  concluir qualquer Journey.
- [Clinical Capability Catalog](clinical-capability-catalog.md) — catálogo
  oficial das capacidades clínicas entregues pelo Astera.
- [Clinical Capability Map](clinical-capability-map.md) — relação entre
  capacidades, participantes, Workflows e Clinical Scenarios.
- [Clinical Workflow Certification](clinical-workflows/README.md) — critérios
  para declarar uma consulta concluída e certificada.
- [Clinical Workflow Dataset](clinical-workflows/clinical-workflow-dataset.md) —
  casos dourados e protocolo de comparação.
- [Platform](platform/README.md) — núcleo estável e boundaries.
- [Capabilities](capabilities/README.md) — produto e certificação.
- [Providers](providers/README.md) — engines substituíveis.
- [Executive Dashboard](executive-dashboard.md) — indicador oficial de estado.
- [Demo Day](demo-day.md) — roteiro de demonstração orientado ao médico.
- [Development Provider Policy](development-provider-policy.md) — política normativa aprovada para desenvolvimento CPU-first.
- [Technology Selection Policy v2](technology-selection-policy-v2.md) — separa Capability Providers de Foundation Models do Google ADK.
- [Astera Benchmark Lab](benchmarks/README.md) — evidências comparáveis de providers.
- [Capability Catalog](capability-catalog.md) — descoberta provider-neutral para ADK e orquestração.
- [RFC-003 — FHIR Strategy](RFC-003-fhir-strategy.md) — proposta de separação entre FHIR Mapper do Astera e validação HAPI.

## Architecture Evolution

O encerramento formal da arquitetura está em [ADR-011 — Platform Complete](../adrs/ADR-011-platform-complete.md).
Novas abstrações estão proibidas; o trabalho ativo ocorre no Product Backlog.

Status operacional: **🟢 ASTERA PLATFORM — ARCHITECTURE FROZEN**. A evolução
ativa passa a ser orientada por jornadas clínicas: Patient Journey, Doctor
Journey, Communication Journey e Consultation Journey. Workbench permanece como nome
interno; o produto é Astera Clinical.

Ordem de produto: Vision Demo → Patient Journey → Doctor Journey →
Communication Journey → Consultation Journey → Clinical Journey → A2UI Journey
→ Clinical Review Journey → Deployment Journey → Operations Journey. A Sprint
atual é **Patient Journey**.

O [Backlog de Evolução Arquitetural do Kernel](kernel-evolution-backlog.md) é
histórico e está encerrado pela ADR-011. Qualquer exceção estrutural futura
segue obrigatoriamente:

```text
Trigger → ADR → Astera Flow → Implementação
```

## Cognitive Architecture

A [especificação formal da Cognitive Architecture](cognitive-architecture/README.md)
consolida workshops, contratos, eventos, cenários de validação e ADRs. O
processo normativo para conceitos cognitivos é:

```text
Workshop → RFC → Architecture Review → Engineering Review
         → Reality Review → Medical Validation
         → ADR → Astera Flow → Implementação
```

O [Cognitive Validation Lab](cognitive-validation-lab/README.md) mantém a
validação permanente do modelo cognitivo separada dos testes de software.

## Construction

A fase de construção está documentada em [Construction](construction/README.md).
Ela implementa os plugins na ordem aprovada pelo Astera Flow, sob o freeze
arquitetural da [ADR-010](../adrs/ADR-010-architecture-freeze.md).

## Capability-first Product Roadmap

Após a Construction, a evolução do produto é acompanhada por
[Capabilities](capabilities/README.md):

```text
Capability → Provider → Plugin → Validation → Certification → Production
```

Foundation Model benchmark e certification ficam separados no [Benchmark Lab](benchmarks/foundation-model-benchmark.md)
e não alteram o lifecycle dos Capability Providers.
