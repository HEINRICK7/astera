# ADR-005: Clinical Context como molécula cognitiva

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team |
| **Categoria** | Cognitive Architecture |
| **Workshop** | Workshop 2 — O Modelo Cognitivo |

## Contexto

O Workshop 1 definiu Clinical Fact como átomo de informação clínica. Fatos
isolados, porém, não representam o estado que um médico interpreta: sintomas,
sinais, histórico, intervenções e respostas se relacionam e mudam ao longo do
tempo.

## Decisão

Adotar **Clinical Context** como a molécula cognitiva do Astera:

```text
Encounter → Clinical Context → Facts + Relationships + Timeline + Hypotheses
```

Clinical Context representa o estado clínico de um paciente durante um
Encounter em uma janela temporal. Ele deve ser versionado, relacional e
proveniente. Uma atualização cria uma nova versão do contexto sem criar outro
paciente, Encounter ou documento clínico.

## Contrato conceitual

```text
ClinicalContext
├── patient
├── encounter
├── facts
├── relationships
├── timeline
├── active_hypotheses
├── confidence
├── version
├── valid_at
└── metadata
```

## Consequências esperadas

- Agentes recebem contexto estruturado em vez de transcript bruto.
- Medical Knowledge consulta o contexto para contextualizar fatos.
- SOAP, FHIR e Timeline são projeções do contexto.
- Relações passam a ser parte do modelo, não apenas uma ordenação de eventos.
- O histórico permanece reconstruível quando fatos e hipóteses evoluem.

## Limites

Clinical Context não contém prompt, LLM, provider, regra de apresentação,
SOAP ou FHIR. Também não transforma automaticamente uma relação em diagnóstico
ou recomendação.

## Governança

Esta ADR foi aprovada pelo Astera Flow. A semântica de relações permanece
extensível dentro dos contratos existentes e não autoriza novos conceitos sem
o fluxo da ADR-010.

## Referências

- [Workshop 2 — Clinical Context](../astera-flow/workshops/workshop-02-clinical-context.md)
- [Workshop 1 — Clinical Facts](../astera-flow/workshops/workshop-01-clinical-facts.md)
- [ADR-004 — Clinical Fact](ADR-004-clinical-fact-as-atomic-unit.md)
