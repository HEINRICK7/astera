# Workshop 5 — Specialists e Clinical Representation

| Campo | Valor |
|---|---|
| **Fase** | C.5 — Cognitive Architecture |
| **Workshop** | 5 — Specialists e Clinical Representation |
| **Status** | Proposed Decision |
| **ADR** | ADR-008 |
| **Pré-requisito** | Workshops 1–4 / ADR-004–007 Proposed |
| **Pergunta central** | Quem toma as decisões e como o Clinical Context é enriquecido? |

## Princípio de trabalho

O Astera não deve concentrar toda a responsabilidade em um agente gigante. Ele
deve organizar especialistas, cada um com uma responsabilidade explícita.
O centro não é o agente nem o ADK: é o `Clinical Context` vivo.

```text
Conversation / exames / APIs
        ↓
Transcript
        ↓
Clinical Facts Specialist
        ↓
Clinical Context
        ↓
Reasoning Specialist
        ↓
Clinical Context enriquecido
        ↓
Knowledge / Gap / Documentation Specialists
        ↓
Clinical Context enriquecido + representações
```

Transcript é uma fonte de extração e auditoria. O Clinical Context é a unidade
canônica de raciocínio e evolui por enriquecimentos versionados.

## Decisão proposta

Adotar um contrato cognitivo central e um envelope operacional:

1. `Clinical Context`, recebido por cada Specialist cognitivo e devolvido como
   uma nova versão enriquecida;
2. `Specialist Invocation`, usado pelo Runtime para identificar a operação,
   o Specialist, a versão de entrada e a proveniência da transformação.

Specialists não conversam diretamente. Eles se comunicam por versões do
Clinical Context. Nenhum enriquecimento pode promover silenciosamente uma
hipótese ou recomendação a Clinical Fact.

## Clinical Context como objeto vivo

```json
{
  "context_id": "ctx-123",
  "context_version": 4,
  "patient": {"id": "patient-123"},
  "encounter": {"id": "enc-456"},
  "assertions": [],
  "relationships": [],
  "timeline": [],
  "hypotheses": [],
  "information_gaps": [],
  "knowledge_references": [],
  "enrichment_state": "hypotheses_and_knowledge",
  "provenance": {}
}
```

O mesmo objeto é enriquecido progressivamente:

```text
Context v1: Facts
      ↓ Clinical Context Specialist
Context v2: Facts + Relationships + Timeline
      ↓ Reasoning Specialist
Context v3: Facts + Relationships + Timeline + Hypotheses
      ↓ Knowledge Specialist
Context v4: ... + Knowledge References + Recommendations
      ↓ Documentation Specialist
Context v5: ... + Representation Manifest
```

Não existem objetos cognitivos paralelos para cada etapa. Existem versões
auditáveis do mesmo Clinical Context.

## Specialists e responsabilidades

| Specialist | Entrada principal | Enriquecimento / saída |
|---|---|---|
| Speech Specialist | Áudio | Transcript e provenance da fonte |
| Clinical Facts Specialist | Transcript e fontes | Clinical Assertions/Facts |
| Context Specialist | Facts | Relationships, timeline e contexto |
| Reasoning Specialist | Clinical Context | Hypotheses, suporte, conflitos e gaps |
| Knowledge Specialist | Context + hipóteses | Knowledge Queries, referências e objetos aplicáveis |
| Gap Detection Specialist | Context + hipóteses | Information Gaps e perguntas propostas |
| Medication Specialist | Context + Knowledge Objects | Interações, contraindicações e referências |
| Documentation Specialist | Clinical Context completo | Manifesto e projeções SOAP, FHIR, Timeline, Referral e Summary |

O Speech Specialist é uma etapa de aquisição antes do primeiro Clinical
Context. A partir da criação do contexto, todo Specialist cognitivo recebe e
devolve contexto versionado. O Runtime mantém a fronteira entre aquisição,
enriquecimento e projeção.

### Campos obrigatórios de cada item clínico

Cada assertion, relação, hipótese, gap e referência deve carregar, diretamente
ou por envelope comum:

```text
Clinical Item
├── id
├── type
├── subject
├── concept / free_text
├── source
├── observed_at / valid_at
├── polarity: positive | negative | unknown
├── certainty: stated | inferred | reported | measured | uncertain
├── status: candidate | supported | contradicted | rejected | active
├── provenance
└── context_version
```

`source` identifica quem ou o que originou o item. `provenance` explica como
ele foi extraído, transformado ou revisado. Temporalidade, polaridade,
certeza e status não devem ser inferidos apenas pela posição do texto.

## Clinical Assertion

`Clinical Assertion` é o envelope conceitual para uma afirmação sobre o
paciente, um evento ou um estado clínico. Ela não substitui Clinical Fact:
uma assertion pode ser candidata, negada, incerta ou contraditória e só se
torna fact conforme a política de validação do contexto.

```text
Clinical Assertion
├── subject: patient / encounter / event
├── concept: dor torácica
├── source: patient_report | clinician | device | document | system
├── observed_at: 2026-08-07T09:00:00-03:00
├── polarity: positive
├── certainty: reported
├── status: candidate
└── provenance: transcript span / author / extraction method
```

### Exemplos de afirmações

| Situação | Representação | Regra |
|---|---|---|
| Paciente afirma dor | `polarity=positive`, `certainty=reported` | Preservar a fonte paciente |
| Paciente nega febre | `polarity=negative`, `certainty=reported` | Negação não é ausência universal |
| Relato incerto | `polarity=unknown`, `certainty=uncertain` | Não usar como suporte forte sem qualificação |
| Exame contradiz hipótese | `status=contradicted` na relação/hipótese | Preservar o fato original e o conflito |

## Specialist Invocation e Context Update

```json
{
  "invocation_id": "inv-789",
  "specialist": "reasoning",
  "context_id": "ctx-123",
  "input_context_version": 4,
  "output_context_version": 5,
  "enrichments": [],
  "provenance": {}
}
```

O resultado cognitivo é o contexto atualizado:

```text
Specialist(Context vN)
        ↓
Context Enrichment
        ↓
Specialist(Context vN+1)
```

O `enrichments` deve declarar itens adicionados, atualizados ou relacionados,
sem apagar o histórico. Uma representação produzida pelo Documentation
Specialist é registrada como manifesto no contexto e emitida como projeção.

O Specialist não deve retornar apenas texto livre como resultado canônico.
Texto livre pode acompanhar a projeção, mas não substitui contexto, tipos,
provenance ou referências.

## Hipótese não vira fato

```text
Specialist(Context vN).hypotheses[]
        ↓ revisão / validação / novo fato
Clinical Context vN+1
        ↓ política explícita
Clinical Fact candidate ou accepted fact
```

Uma hipótese pode mencionar uma doença, mas isso não registra a doença como
diagnóstico do paciente. Uma recomendação pode citar um medicamento, mas isso
não cria uma prescrição. Uma pergunta proposta não é uma ordem clínica.

## Clinical Representation

SOAP, FHIR, Timeline, encaminhamento e resumo são representações derivadas.
Cada uma deve declarar:

```text
Representation
├── type: soap | fhir | timeline | referral | summary
├── source_context_id
├── source_context_version
├── included_items
├── omitted_items / omission_reason
├── generated_at
├── authoring_agent
├── status: draft | reviewed | published
└── provenance
```

Uma representação não deve apagar facts, hipóteses, conflitos, gaps ou
referências que ficaram fora do formato de destino. FHIR é uma saída de
interoperabilidade; SOAP é uma saída documental; nenhum dos dois substitui o
Clinical Context.

## Papel dos Specialists e do ADK no CRL

```text
Clinical Context vN
  ↓
Specialist selecionado pelo Runtime
  ↓
Enriquece uma responsabilidade única
  ↓
Clinical Context vN+1
  ↓
Próximo Specialist recebe o contexto
```

O ADK conhece apenas a coordenação do Clinical Context e do ciclo de
enriquecimento. Ele não precisa conhecer SOAP, FHIR, Timeline, PDF ou
prontuário. O Runtime mantém a autoridade sobre transições de estado,
provenance, versionamento e publicação.

## Limites arquiteturais

O modelo de Specialists não deve:

- exigir transcript bruto para raciocínio;
- aceitar diagnóstico implícito em texto como fato;
- misturar Medical Knowledge com Clinical Facts;
- esconder fonte, temporalidade, certeza, polaridade ou status;
- publicar SOAP/FHIR como verdade canônica;
- omitir conflitos, lacunas ou contraindicações das referências;
- permitir comunicação direta que contorne o Clinical Context;
- delegar ao LLM ou ao ADK a autoridade de persistir ou promover estado clínico.

## Resultado do Workshop 5

**Proposed Decision:** o Astera organiza Specialists de responsabilidade única.
Cada Specialist cognitivo recebe um Clinical Context e devolve uma versão
enriquecida do mesmo objeto. O ADK coordena o enriquecimento e não conhece os
formatos de representação. Clinical Assertions, hipóteses, gaps, perguntas,
Knowledge Queries e representações permanecem entidades distintas, com
provenance explícita.

A decisão aguarda ADR-008 e aprovação explícita do Astera Flow. Nenhum contrato
de código será criado nesta etapa conceitual.
