---
document_id: astera-construction
title: Construction
category: Engineering
status: Official
version: 2.0
owner: Astera Engineering
depends_on:
  - ../product-backlog.md
  - ../../adrs/ADR-011-platform-complete.md
used_by:
  - Product Engineering
  - Engineering
last_updated: 2026-08-07
---

# Construction

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Fase** | Construction |
| **Versão arquitetural** | 1.0 — completa pela ADR-011 |
| **Fonte de verdade** | Astera Flow |
| **Validação de software** | pytest |
| **Validação cognitiva** | Cognitive Validation Lab |

## Objetivo histórico

Transformar a arquitetura aprovada em plugins executáveis, preservando o
Kernel, os contratos, os eventos e as boundaries existentes. Essa fase está
encerrada e os sprints abaixo são registro histórico da fundação.

## Builders

Os agentes desta fase atuam como Builders. Implementam o que está especificado,
sem introduzir conceitos cognitivos novos. Uma limitação real encontrada pelo
Cognitive Validation Lab é encaminhada pelo fluxo da ADR-010.

Após a conclusão da Construction, os agentes operam como Product Engineers. O
trabalho ativo está no [Product Backlog](../product-backlog.md), sob a ADR-011.

## Sprints técnicos encerrados

| Sprint | Módulo | Status | Resultado esperado |
|---:|---|---|---|
| 1 | Speech Plugin | Completed | Transcript provider-neutral integrado ao Runtime |
| 2 | Clinical Facts Plugin | Completed | Clinical Fact candidate rastreável a NLP/provenance |
| 3 | Context Builder | Completed | Clinical Context versionado com facts e timeline |
| 4 | Reasoning Plugin | Completed | Hypotheses e Information Gaps conforme CRL |
| 5 | Knowledge Plugin | Completed | Knowledge Query e referências versionadas |
| 6 | Documentation Plugin | Completed | SOAP/FHIR como representações derivadas |
| 7 | End-to-End Consultation | Completed | Harness da consulta completa integrado |

Esses sprints não são mais o backlog ativo. “Speech”, “OCR” ou qualquer outro
componente só pode receber trabalho novo quando estiver vinculado a um CPI no
[Product Backlog](../product-backlog.md).

## Unidade ativa de entrega

O trabalho atual é organizado assim:

\`\`\`text
CPI clínico → caso dourado → jornada executável → revisão médica → certificação
\`\`\`

Uma tarefa técnica é válida quando possui vínculo explícito:

| Campo obrigatório | Exemplo |
|---|---|
| CPI | CPI-001 — Primary Care Consultation |
| Fatia clínica | CPI-001.C — Documentar consulta |
| Etapa habilitada | SOAP |
| Evidência esperada | SOAP revisável e rastreável ao Context |
| Critério de saída | Médico consegue revisar e corrigir sem logs técnicos |

## Definition of Done

Cada sprint só é concluída quando possui:

- implementação no boundary correto;
- contratos imutáveis e validações de entrada;
- testes unitários e de integração com o Runtime;
- lifecycle de plugin, provider health e capability registry;
- logs/observabilidade sem dados clínicos sensíveis;
- registro no Engineering Journal;
- execução do pytest sem regressões.

## Gates operacionais

O status do trabalho ativo é controlado pelo CPI. Não há promoção de produto
por checkpoint de componente isolado.

```text
CPI → Contrato existente → Implementação habilitadora → pytest → Integração
→ Clinical Replay → CQA/Medical Validation → Astera Flow atualiza o próximo CPI
```

## Referências

- [ADR-010 — Architecture Freeze](../../adrs/ADR-010-architecture-freeze.md)
- [ADR-011 — Platform Complete](../../adrs/ADR-011-platform-complete.md)
- [Agent Execution Plan](../agent-execution-plan.md)
- [Cognitive Validation Lab](../cognitive-validation-lab/README.md)
