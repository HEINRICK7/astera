# Failure Analysis

| Campo | Valor |
|---|---|
| **Status** | Proposed |
| **Responsável** | Gap Detector + Architecture Reviewer |

## Objetivo

Transformar uma falha observada em uma decisão clara: lacuna de anotação,
problema de contrato, erro de implementação ou mudança arquitetural.

## Taxonomia

| Classe | Pergunta |
|---|---|
| Information Loss | O modelo perdeu informação relevante? |
| Information Invention | Criou fact, relação, hipótese ou recomendação inexistente? |
| Concept Confusion | Misturou Fact, Evidence, Knowledge, Hypothesis ou Representation? |
| Boundary Failure | Specialist ou camada assumiu responsabilidade de outro? |
| Temporal Failure | Perdeu ordem, duração, retorno ou atualização? |
| Query Timing Failure | Consultou Knowledge no momento errado ou sem necessidade? |
| Question Value Failure | Pergunta não reduziu gap relevante? |
| Representation Drift | SOAP/FHIR deixou de refletir o Context? |
| Lifecycle Failure | Estado ou transição não foi representado? |
| Event Failure | Evento ausente, duplicado ou sem provenance? |

## Decision Record

```text
failure_id
case_id / session_id
observed_behavior
expected_behavior
affected_concept
severity: low | medium | high | critical
root_cause: model | contract | implementation | source | annotation
architecture_change_needed: yes | no | undecided
recommended_action
reviewer
status
```

## Regra

O Gap Detector identifica o que faltou. O Architecture Reviewer decide se a
falha altera RFC/ADR ou se pode ser corrigida na implementação. Nenhum dos dois
agentes escreve código.
