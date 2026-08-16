# Workshop 2 — Clinical Context

| Campo | Valor |
|---|---|
| **Fase** | C.5 — Cognitive Architecture |
| **Workshop** | 2 — O Modelo Cognitivo |
| **Status** | Proposed Decision |
| **ADR** | ADR-005 |
| **Pré-requisito** | Workshop 1 / ADR-004 Proposed |
| **Pergunta central** | Como Clinical Facts viram conhecimento contextual? |

## Princípio de trabalho

Um médico não interpreta Clinical Facts isolados. Ele relaciona dor, falta de
ar, sudorese, idade, hipertensão e tabagismo em um contexto clínico que evolui
ao longo do tempo.

```text
Clinical Fact
   ↓
Relaciona
   ↓
Relaciona
   ↓
Hipóteses
   ↓
Perguntas
   ↓
Novos Clinical Facts
   ↓
Descarta ou confirma hipóteses
   ↓
Plano
```

## Decisão proposta

O centro cognitivo do Astera será o **Clinical Context**:

> A representação temporal e relacional do estado clínico de um paciente
> durante um Encounter.

Clinical Context é a molécula; `Clinical Fact` continua sendo o átomo.

## Estrutura conceitual

```text
Encounter
  ↓
Clinical Context
  ├── Facts
  ├── Relationships
  ├── Timeline
  ├── Active Hypotheses
  ├── Confidence
  └── Metadata
```

O contexto deve carregar `patient`, `encounter`, janela temporal, versão do
snapshot e provenance suficiente para reconstruir como o estado foi formado.

## Exemplo de contexto

```text
Clinical Context
├── Fact: Dor no peito
├── Fact: Falta de ar
├── Fact: Tabagismo
├── Fact: Hipertensão
├── Fact: Sudorese
└── Relationships
    ├── Dor no peito ── associada ── Sudorese
    ├── Dor no peito ── piora com ── esforço
    └── Hipertensão ── fator de risco para ── dor torácica
```

O contexto não é uma lista ordenada de fatos. É um estado composto por fatos,
relações e hipóteses ativas.

## Evolução temporal

```text
09:00  Dor 5/10
  ↓
09:20  Dor 9/10
  ↓
09:40  Nitroglicerina → Dor 2/10
```

Isso representa a evolução do mesmo Clinical Context. Não cria outro paciente,
outro Encounter ou outro SOAP. Cria uma nova versão temporal do contexto,
preservando as versões anteriores para auditoria.

## Clinical Context como grafo temporal

```text
Encounter
  ↓
Clinical Context v1
  ├── Facts at 09:00
  └── Relationships observed at 09:00
       ↓ new facts / observations
Clinical Context v2
  ├── Facts at 09:20
  ├── Updated relationships
  └── Active hypotheses
       ↓ intervention / response
Clinical Context v3
  ├── Facts at 09:40
  ├── Response to intervention
  └── Hypothesis status changes
```

O contexto é uma visão versionada do grafo; o grafo não deve apagar fatos ou
relações históricas quando o estado atual mudar.

## Consumidores do Clinical Context

```text
Clinical Context
├── Agent recebe
├── Medical Knowledge consulta
├── Clinical Reasoning interpreta
├── SOAP projeta
├── FHIR projeta
├── Timeline registra
└── ADK orquestra
```

Transcript é uma fonte de facts. Não é o contexto que o agente deve receber
como unidade principal.

## Limites arquiteturais

Clinical Context não deve:

- conter prompt ou chamada a LLM;
- depender de Google ADK;
- conhecer formato SOAP ou FHIR;
- virar uma tabela plana sem relações;
- substituir provenance dos fatos;
- concluir diagnóstico automaticamente só por conter relações.

Clinical Reasoning usa o contexto para criar e atualizar hipóteses. Uma
hipótese permanece distinta de fato e precisa de suporte e status próprios.

## Relações usadas pelo raciocínio

O Workshop 2 identifica relações como necessidade do modelo, mas não fecha sua
semântica. O Clinical Reasoning Loop precisará trabalhar com relações como:

- causa;
- agrava;
- melhora com;
- ocorre após;
- contradiz;
- confirma;
- fator de risco para;
- consequência de.

A semântica formal, a força e a direção dessas relações serão refinadas junto
com o modelo de raciocínio e permanecem decisões abertas.

## Resultado do Workshop 2

**Proposed Decision:** Clinical Context é o centro cognitivo do Astera e a
molécula que organiza fatos, relações, timeline e hipóteses ativas. A decisão
aguarda ADR-005 e aprovação explícita do Astera Flow.
