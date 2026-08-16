# ADR-003: Workshops de Cognitive Architecture antes da implementação

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team |
| **Categoria** | Cognitive Architecture |
| **Fase proposta** | C.5 |

## Contexto

O Runtime já possui componentes de Speech, Evidence, Knowledge,
Representation e agentes, mas o vocabulário cognitivo ainda pode misturar
transcrição, fatos, evidência, hipóteses e conhecimento médico. Implementar
mais agentes antes de resolver essas fronteiras aumentaria o risco de contratos
incompatíveis e perda de provenance.

## Proposta

Criar a Fase C.5 — Cognitive Architecture, antes da Fase D, composta por cinco
workshops:

1. Clinical Facts
2. Clinical Context / Modelo Cognitivo
3. Clinical Reasoning Model / Clinical Reasoning Loop
4. Medical Knowledge Layer
5. Specialists e Clinical Representation

O Workshop 6 — End-to-End Clinical Encounter valida os cinco workshops em um
cenário completo antes de qualquer implementação.

Essa fase produz modelos, glossário, decisões, ADRs e critérios conceituais.
Não produz código.

Os resultados normativos são consolidados na [RFC-001](../astera-flow/cognitive-architecture/RFC-001-astera-cognitive-architecture.md)
e no domínio [Cognitive Architecture](../astera-flow/cognitive-architecture/README.md).

## Estado atual

Esta ADR foi aprovada pelo Astera Flow e sua especificação está consolidada na
Construction. A implementação segue a ADR-010.

## Hipótese de trabalho

Uma `Clinical Assertion` é candidata a unidade fundamental: uma afirmação sobre
um paciente, evento ou estado clínico, com origem, temporalidade, polaridade,
certeza, provenance e status. Essa hipótese será validada no Workshop 1 e não
é uma decisão de implementação.

## Consequências

- O vocabulário cognitivo será decidido antes de novos contratos de agente.
- Knowledge externo e estado do paciente permanecerão separados.
- FHIR, SNOMED CT, LOINC e RxNorm serão usados conforme seus papéis, não como
  uma única camada semântica.
- A Fase D não deve receber novos contratos cognitivos derivados desta proposta
  antes da decisão do Astera Flow.

## Referências

- [Fase C.5 — Cognitive Architecture](../astera-flow/cognitive-architecture-phase.md)
- [Research Notes](../astera-flow/cognitive-architecture-research.md)
- [ADR-002 — Architecture Evolution Governance](ADR-002-architecture-evolution-governance.md)
