# ASTERA_INDEX.md

> Master Navigation Document
>
> Este documento é o ponto oficial de entrada para qualquer agente de IA ou desenvolvedor.
>
> Nenhum agente deve iniciar a implementação sem seguir esta sequência.

---

# Objetivo

O Astera possui diversos documentos.

Este índice define:

- ordem de leitura;
- prioridade;
- dependências;
- documentos obrigatórios;
- documentos opcionais.

Este documento elimina ambiguidades durante a implementação.

## Precedência normativa

Em caso de conflito, prevalece esta ordem:

1. Constituição de Engenharia (`docs/engineering/ASTERA-ENG-*.md`);
2. ADRs;
3. `AGENTS.md`;
4. documentação complementar.

Essa precedência foi instituída pelo [ADR-015 — Engineering Governance](adrs/ADR-015-engineering-governance.md).
Uma regra antiga que impeça auditoria, integração ou validação correta do
Runtime deve ser atualizada explicitamente, com justificativa registrada.

---

# Ordem Oficial de Leitura

1. AGENTS.md
2. ASTERA_INDEX.md
3. DOCUMENT_CONVENTIONS.md
4. GLOSSARY.md
5. README.md
6. Architecture
7. Engineering
8. Knowledge
9. Product
10. ADRs
11. Astera Flow

---

# Documentos Obrigatórios

Todos os agentes devem ler obrigatoriamente:

- AGENTS.md
- ASTERA_INDEX.md
- DOCUMENT_CONVENTIONS.md
- GLOSSARY.md
- README.md
- Astera Flow
- Constituição de Engenharia (`docs/engineering/README.md` e documentos
  `ASTERA-ENG` aplicáveis)

---

# Categorias

## Constituição

Define regras permanentes.

- [Constituição de Engenharia](engineering/README.md)
- AGENTS.md
- ASTERA_INDEX.md

---

## Arquitetura

Define como a plataforma funciona.

- Architecture
- ADRs

## Runtime

O mapa de execução e a regra contra pipelines paralelos estão em:

- [Astera Runtime](runtime/RUNTIME.md)
- [ASTERA-SPR-001 — Runtime Validation](engineering/ASTERA-SPR-001-runtime-validation.md)

---

## Engenharia

Define como construir.

- Engineering
- Astera Flow

Constituição de engenharia:

- [Engineering README](engineering/README.md)
- [Runtime Definition of Done](engineering/ASTERA-ENG-001-runtime-definition-of-done.md)
- [Runtime Audit](engineering/ASTERA-ENG-002-runtime-audit.md)
- [Runtime Integration Contract](engineering/ASTERA-ENG-003-runtime-integration-contract.md)
- [Execution Trace](engineering/ASTERA-ENG-004-execution-trace.md)
- [Provider Governance](engineering/ASTERA-ENG-005-provider-governance.md)
- [End-to-End Validation](engineering/ASTERA-ENG-006-end-to-end-validation.md)
- [Runtime Observability](engineering/ASTERA-ENG-007-runtime-observability.md)
- [Architecture Drift](engineering/ASTERA-ENG-008-architecture-drift.md)
- [Source of Truth](engineering/ASTERA-ENG-009-source-of-truth.md)
- [Release Gate](engineering/ASTERA-ENG-010-release-gate.md)
- [Engineering Workflow](engineering/ASTERA-ENG-011-engineering-workflow.md)
- [ASTERA-SPRINT-000 — Runtime Alignment](engineering/ASTERA-SPRINT-000-runtime-alignment.md)

---

## Conhecimento

Define fontes.

- Knowledge

---

## Produto

Define visão.

- Product

---

# Dependências

Antes de implementar um módulo, verificar seus documentos relacionados.

Exemplo:

Plugin

↓

Architecture

↓

Engineering

↓

Astera Flow

---

# Regra

Nunca implementar utilizando apenas conhecimento do modelo.

Sempre utilizar o Astera Flow como fonte principal.

---

# Objetivo Final

Garantir que todos os agentes utilizem exatamente a mesma sequência de leitura e implementação.
