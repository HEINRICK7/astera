# RFC-002 — Clinical Graph Architecture

| Campo | Valor |
|---|---|
| Status | Proposed |
| Owner | Astera Architecture |
| Impact | High |
| Priority | Era 4 — Clinical Product |
| Scope | Clinical domain only |

## Objetivo

Adicionar uma representação semântica intermediária que organize Clinical
Facts em nós e relacionamentos clínicos explícitos:

```text
Transcript → Clinical Facts → Clinical Graph → Clinical Context → Reasoning
                                               ↓
                                      Knowledge / SOAP / FHIR
```

Clinical Facts permanecem a fonte da verdade. O Graph não os substitui nem
altera os contratos públicos existentes.

## Limites arquiteturais

O RFC não altera Kernel, Google ADK, Capabilities, Foundation Models, Provider
SDKs ou contratos públicos. O Clinical Graph pertence exclusivamente ao
domínio clínico.

Tipos iniciais de nós: `symptom`, `condition`, `medication`, `observation`,
`allergy`, `exam`, `procedure` e `lifestyle`.

Relacionamentos iniciais: `HAS_LOCATION`, `HAS_DURATION`, `HAS_SEVERITY`,
`HAS_MEDICATION`, `HAS_DOSAGE`, `HAS_FREQUENCY`, `HAS_TRIGGER`, `HAS_RELIEF`,
`SUPPORTS` e `CONFLICTS`.

## Roadmap proposto

1. Sprint 1 — modelos, builders, relacionamentos e validação.
2. Sprint 2 — Clinical Context consumir Graph.
3. Sprint 3 — Reasoning consumir Graph.
4. Sprint 4 — Knowledge consumir Graph.
5. Sprint 5 — SOAP consumir Graph.
6. Sprint 6 — FHIR consumir Graph.

## Implementação atual

O Sprint 1 foi criado como scaffold isolado em
`packages/clinical_graph_sdk`. Ele constrói Graphs a partir de
`ClinicalFactsBatch`, preserva todos os `source_fact_ids` e valida referências
de nós e arestas. Ainda não está conectado ao CPI-001, Context, Reasoning,
SOAP ou FHIR.

Os Sprints 2–6 permanecem bloqueados até Architecture Review, Medical
Validation, ADR e aprovação do Astera Flow.
