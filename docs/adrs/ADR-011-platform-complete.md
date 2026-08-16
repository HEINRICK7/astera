# ADR-011 — Platform Complete

Status: **Accepted**  
Date: 2026-08-07  
Related: [ADR-010 — Architecture Freeze](ADR-010-architecture-freeze.md)

## Contexto

O Astera possui arquitetura Hexagonal, Provider-Oriented, Foundation Model
Boundary, Capability Layer, Provider Layer, Tool Layer, Kernel, governança
Astera Flow, Research, Benchmark, Certification e Cognitive Validation Lab.

A última extensão aprovada foi o `ToolAdapter` e o `CapabilityCatalog`. Ambos
foram implementados sem alteração de contratos públicos e validados pela suíte
de testes.

## Decisão

A arquitetura base da plataforma é considerada **completa**.

Novas abstrações arquiteturais ficam proibidas. A evolução futura deverá
ocorrer através de:

- novos Development, Benchmark ou Production Providers;
- novos Foundation Models através de adapters existentes;
- novas Capabilities somente quando surgir um domínio comprovadamente novo;
- melhorias internas sem alteração dos contratos públicos;
- integração, benchmark, Medical Validation, CQA e certificação de workflows.

Qualquer mudança estrutural exigirá evidência concreta de uma integração real,
limitação do Google ADK ou falha estrutural demonstrada pelo Cognitive
Validation Lab. A evidência deverá seguir o fluxo vigente de ADR e Astera Flow.

## Consequências

- Agents passam de Architecture Engineers para **Product Engineers**.
- O backlog oficial passa a ser o [Product Backlog](../astera-flow/product-backlog.md).
- Uma entrega deve resultar em capacidade utilizável, evidência ou certificação
  de produto.
- A ausência de uma Capability real não autoriza criar arquitetura especulativa.

## Regra operacional

Antes de iniciar qualquer tarefa, o Agent deve responder:

> Esta entrega cria ou melhora uma capacidade utilizável pelo usuário final,
> uma evidência de qualidade ou uma certificação?

Se a resposta for não, a tarefa não entra no Product Backlog sem aprovação
explícita do Astera Flow.
