---
document_id: astera-engineering-constitution
title: Constituição de Engenharia do Astera
category: Engineering
status: Official
version: 1.0
owner: Astera Engineering
depends_on:
  - ../AGENTS.md
  - ../DOCUMENT_CONVENTIONS.md
  - ../ASTERA_INDEX.md
used_by:
  - Product Engineering
  - Runtime Engineering
  - Clinical Validation
  - Release Engineering
last_updated: 2026-08-10
---

# Constituição de Engenharia do Astera

Este diretório reúne as regras obrigatórias para transformar uma decisão
arquitetural em comportamento comprovado no Runtime e na interface.

Instituição normativa: [ADR-015 — Engineering Governance](../adrs/ADR-015-engineering-governance.md).

Todos os agentes, desenvolvedores e processos de revisão devem seguir estes
documentos. Nenhuma funcionalidade pode ser considerada concluída sem cumprir
as normas aplicáveis.

## Documentos normativos

| Documento | Regra |
|---|---|
| [ASTERA-ENG-001](ASTERA-ENG-001-runtime-definition-of-done.md) | Estados obrigatórios de uma feature |
| [ASTERA-ENG-002](ASTERA-ENG-002-runtime-audit.md) | Auditoria técnica sem alteração de código |
| [ASTERA-ENG-003](ASTERA-ENG-003-runtime-integration-contract.md) | Cadeia de integração completa |
| [ASTERA-ENG-004](ASTERA-ENG-004-execution-trace.md) | Trace observável de execução |
| [ASTERA-ENG-005](ASTERA-ENG-005-provider-governance.md) | Estado e seleção de providers |
| [ASTERA-ENG-006](ASTERA-ENG-006-end-to-end-validation.md) | Validação end-to-end sem mocks |
| [ASTERA-ENG-007](ASTERA-ENG-007-runtime-observability.md) | Métricas por camada |
| [ASTERA-ENG-008](ASTERA-ENG-008-architecture-drift.md) | Detecção de divergência arquitetural |
| [ASTERA-ENG-009](ASTERA-ENG-009-source-of-truth.md) | Consulta real como fonte da verdade |
| [ASTERA-ENG-010](ASTERA-ENG-010-release-gate.md) | Gate de encerramento e release |
| [ASTERA-ENG-011](ASTERA-ENG-011-engineering-workflow.md) | Fluxo obrigatório de engenharia |

## Princípio central

```text
ADR
  ↓
Arquitetura
  ↓
Implementação
  ↓
Integração
  ↓
Consulta real
  ↓
Evidência
  ↓
Release
```

Código compilando ou teste unitário passando não comprova integração.
Sem validação em consulta real, a feature permanece incompleta.

## Relatório da Sprint de estabilização

- [ASTERA-SPRINT-000 — Platform Stabilization & Runtime Alignment](ASTERA-SPRINT-000-runtime-alignment.md)
- [ASTERA-SPR-001 — Runtime Validation](ASTERA-SPR-001-runtime-validation.md)
