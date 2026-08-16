# Astera Flow — Fase C.5: Cognitive Architecture

| Campo | Valor |
|---|---|
| **Status** | Proposed |
| **Fase anterior** | C — Core Platform |
| **Fase seguinte** | D — Google ADK |
| **Código nesta fase** | Nenhum |
| **Objetivo** | Modelar como o Astera representa, valida e transforma conhecimento clínico |
| **Autoridade** | Astera Flow + ADR-003 |

> Esta é uma proposta de arquitetura cognitiva. Ela não altera a ordem oficial
> das fases nem autoriza implementação até que o Astera Flow a aprove.

Especificação formal: [Cognitive Architecture](cognitive-architecture/README.md)
e [RFC-001](cognitive-architecture/RFC-001-astera-cognitive-architecture.md).

## Objetivo

Definir o modelo conceitual que conecta uma conversa clínica a fatos,
evidências, contexto, conhecimento, hipóteses, validação e representação
clínica. A fase deve produzir decisões de modelagem, vocabulário compartilhado,
invariantes e ADRs; não deve produzir classes, endpoints ou plugins.

## Pipeline cognitivo proposto

```text
Patient
  ↓
Conversation
  ↓
Transcript
  ↓
Clinical Fact Candidates
  ↓
Evidence
  ↓
Clinical Context
  ↓
Knowledge
  ↓
Clinical Reasoning
  ↓
Hypotheses
  ↓
Validation
  ↓
Clinical Representation
  ├── SOAP
  ├── FHIR
  └── Timeline
```

O desenho separa observação, interpretação, conhecimento externo e documento
final. Nenhuma etapa posterior deve apagar a proveniência da etapa anterior.

## Cinco workshops e uma validação ponta a ponta

### Workshop 1 — Clinical Facts

**Pergunta central:** qual é a unidade fundamental de informação clínica do Astera?

**Decidir:**

- quais são as fronteiras entre Conversation, Transcript, Fact, Evidence,
  Context, Knowledge, Hypothesis e Representation;
- quais transições são automáticas, revisáveis ou exclusivamente clínicas;
- quais metadados são obrigatórios em cada transição;
- o que pode ser descartado e o que precisa permanecer auditável.

**Saída esperada:** mapa de estados, glossário e invariantes de proveniência.

**Decisão proposta registrada:** `Clinical Fact` como unidade atômica de
informação clínica. A decisão permanece `Proposed` na [ADR-004](../adrs/ADR-004-clinical-fact-as-atomic-unit.md).

### Workshop 2 — O Modelo Cognitivo

**Pergunta central:** como Clinical Facts viram conhecimento contextual?

**Decisão proposta registrada:** `Clinical Context` como molécula que reúne
facts, relationships, timeline e active hypotheses. A decisão permanece
`Proposed` na [ADR-005](../adrs/ADR-005-clinical-context-as-cognitive-molecule.md).

**Saída esperada:** modelo temporal e relacional do contexto clínico.

### Workshop 3 — Clinical Reasoning Model

**Pergunta central:** como nasce uma hipótese clínica?

**Decidir:**

- modelo de Clinical Hypothesis com suporte, lacunas e conflitos;
- modelo de Information Gap e planejamento de perguntas;
- ciclo Observe → Interpret → Hypothesize → Ask → Update Context → Refine;
- papel do ADK como coordenador do loop, não como gerador direto de SOAP.

**Saída esperada:** Clinical Reasoning Loop, hipóteses concorrentes e lacunas
de informação.

**Decisão proposta registrada:** `Clinical Reasoning Loop` na [ADR-006](../adrs/ADR-006-clinical-reasoning-loop.md).

### Workshop 4 — Medical Knowledge Layer

**Pergunta central:** o que pertence à Medical Knowledge Layer?

**Decidir:**

- protocolos, diretrizes, artigos, consensos, medicamentos, interações,
  exames e terminologias;
- diferença entre conhecimento externo versionado e fato específico do
  paciente;
- autoridade, data de vigência, jurisdição, população e nível de evidência;
- quando SNOMED CT, LOINC, RxNorm, CID-10 e FHIR são usados, mapeados ou
  apenas exportados.

**Saída esperada:** mapa de domínios da Knowledge Layer e política de
  versionamento/licenciamento.

**Decisões propostas registradas:** separação entre Clinical World e Medical
World, `Knowledge Query`, `Knowledge Object`, snapshots imutáveis e ADK como
mediador na [ADR-007](../adrs/ADR-007-medical-knowledge-layer.md).

### Workshop 5 — Specialists e Clinical Representation

**Pergunta central:** quem toma as decisões e como o Clinical Context é enriquecido?

**Decidir:**

- se Specialists recebem e devolvem versões enriquecidas do Clinical Context;
- quais responsabilidades pertencem a Speech, Facts, Context, Reasoning,
  Knowledge, Gap Detection, Medication e Documentation Specialists;
- como o ADK coordena o contexto sem conhecer SOAP, FHIR ou prontuário;
- como cada item carrega origem, certeza, temporalidade e status;
- como o agente expressa uma hipótese sem promovê-la a fato;
- como citações, contraindicações e lacunas de informação aparecem na saída.

**Formato de trabalho:**

```json
{
  "context_id": "...",
  "context_version": 4,
  "facts": [],
  "relationships": [],
  "timeline": [],
  "hypotheses": [],
  "knowledge_references": [],
  "provenance": {}
}
```

**Saída esperada:** contrato conceitual de Specialists, enriquecimento
versionado do Clinical Context e manifesto de Clinical Representations, ainda
sem conversão em código.

**Decisão proposta registrada:** Specialists e Clinical Context como objeto de
enriquecimento na [ADR-008](../adrs/ADR-008-agent-context-and-clinical-representation.md).

### Workshop 6 — End-to-End Clinical Encounter

**Pergunta central:** como um atendimento completo evolui do primeiro “Olá” até
a assinatura final do médico?

**Saída esperada:** cenário de validação ponta a ponta usando apenas os
conceitos dos Workshops 1–5, registrado em [Validation Scenarios](cognitive-architecture/08-validation-scenarios.md).

A execução da revisão está em [Architecture Review](cognitive-architecture/10-architecture-review.md)
e [Clinical Simulation](cognitive-architecture/11-clinical-simulation.md).

A etapa seguinte é a [Reality Review](cognitive-architecture/12-reality-review.md),
com o [Reality Case Registry](cognitive-architecture/13-reality-case-registry.md),
antes da Medical Validation.

## Hipótese de trabalho — não aprovada

Para orientar a discussão, a unidade candidata é uma **Clinical Assertion**:
uma afirmação sobre um paciente, evento ou estado clínico, sempre acompanhada
de proveniência, temporalidade, polaridade, certeza e status.

```text
Clinical Assertion
├── subject
├── concept / free text
├── source
├── time
├── polarity
├── certainty
├── provenance
└── status: candidate | supported | contradicted | rejected
```

Essa hipótese não deve ser tratada como decisão final antes dos workshops.
Ela existe para tornar a primeira discussão concreta e evitar que Transcript,
Evidence, Fact e Hypothesis sejam usados como sinônimos.

## Critérios de saída da proposta

Os workshops estarão prontos para decisão do Astera Flow quando houver:

- glossário sem sobreposição entre as entidades cognitivas;
- exemplos de afirmação positiva, negada, incerta e contraditória;
- matriz de proveniência e temporalidade;
- separação formal entre conhecimento externo e estado do paciente;
- contrato conceitual do agente;
- ADRs identificadas e decisões pendentes explicitadas.

Esses são resultados esperados da proposta, não novos bloqueios de execução.
