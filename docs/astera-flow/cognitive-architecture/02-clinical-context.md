# 02 — Clinical Context

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Workshop origem** | Workshop 2 — O Modelo Cognitivo |
| **ADR** | ADR-005 |
| **Responsável** | Context Specialist / Runtime |

## Objetivo

Definir a molécula cognitiva que reúne fatos, relações, timeline, hipóteses,
lacunas e metadata de um paciente durante um Encounter.

## Definições

- **Context:** estado clínico composto em uma janela temporal.
- **Version:** snapshot ordenado sem apagar versões anteriores.
- **Relationship:** ligação semântica e temporal entre itens do contexto.

## Entidade

```text
ClinicalContext
├── context_id / version
├── patient / encounter
├── facts / relationships / timeline
├── active_hypotheses / information_gaps
├── knowledge_references / recommendations
├── valid_at / provenance
└── metadata
```

## Diagrama

```text
Encounter → Context v1 → Context v2 → Context v3
              Facts       Relations    Hypotheses
```

## Contrato normativo

O Context MUST ser temporal, versionado e reconstruível. Uma atualização MUST
produzir `Context vN+1`, preservando `Context vN`; não cria paciente, Encounter
ou SOAP novo.

```text
Encounter → Context v1 → Context v2 → Context v3
              facts       relations    hypotheses
```

## Responsabilidades e eventos

O Context Specialist organiza fatos e relações. O Runtime é responsável por
versionamento e merge autorizado. Eventos mínimos: `clinical.context.created`,
`clinical.context.enriched` e `clinical.context.conflict_detected`.

## Regras e restrições

1. Context MUST NOT ser uma lista plana sem relações e temporalidade.
2. Context MUST NOT depender de prompt, LLM, ADK, SOAP ou FHIR.
3. Facts históricos não podem ser removidos para representar estado atual.
4. Hipóteses e recomendações devem permanecer distintas de facts.

## Exemplo

```text
09:00 Context v1: dor 5/10
09:20 Context v2: dor 9/10 + dispneia + relações
09:40 Context v3: nitroglicerina → dor 2/10 + resposta temporal
```

## Validação

O cenário deve reconstruir o contexto em qualquer versão, preservar conflitos,
localizar a origem de cada item e permitir que Agent/Specialist/Knowledge,
SOAP, FHIR e Timeline consumam o mesmo objeto.

## Questões abertas

Semântica formal das relações, política de merge concorrente, armazenamento e
retenção são decisões posteriores; não alteram o contrato conceitual.
