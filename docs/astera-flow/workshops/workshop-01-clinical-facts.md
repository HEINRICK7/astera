# Workshop 1 — Clinical Facts

| Campo | Valor |
|---|---|
| **Fase** | C.5 — Cognitive Architecture |
| **Workshop** | 1 — O Pipeline Cognitivo |
| **Status** | Proposed Decision |
| **ADR** | ADR-004 |
| **Código** | Nenhum |
| **Pergunta central** | Qual é a unidade fundamental de informação clínica do Astera? |

## Princípio de trabalho

Uma consulta não começa criando SOAP, FHIR ou CID. O paciente produz uma
afirmação clínica. Speech produz uma transcrição. NLP pode produzir uma
entidade. O que precisa atravessar o restante da plataforma é a informação
clínica estruturada, rastreável e independente de representação.

## Decisão proposta

O átomo de informação clínica do Astera será chamado **Clinical Fact**:

> A menor unidade de informação clínica verificável, contextualizada e
> rastreável da plataforma.

Exemplos:

- `Tenho febre.`
- `Minha mãe morreu de câncer.`
- `Estou tomando Losartana.`
- `Tenho alergia à dipirona.`
- `Fumo um maço por dia.`
- `Peso 82 kg.`

Clinical Fact não é sinônimo de texto, entidade NLP, SOAP, FHIR ou CID.

## Clinical Fact versus Clinical Evidence

| Conceito | Papel |
|---|---|
| **Clinical Fact** | Informação observada, informada, medida ou importada sobre o paciente/encounter |
| **Clinical Evidence** | Suporte que aumenta ou reduz a força de uma hipótese ou recomendação |
| **Medical Knowledge** | Conhecimento externo, versionado e referenciável |
| **Clinical Reasoning** | Processo de interpretar fatos com contexto e conhecimento |
| **Hypothesis** | Explicação provisória construída a partir de fatos/evidências |
| **Clinical Recommendation** | Resultado acionável do raciocínio, sujeito a validação clínica |

O nome `Evidence` existente no código é considerado nomenclatura transitória
até a decisão da ADR-004 no Astera Flow. Nenhum rename será feito nesta fase.

## Categorias de Clinical Fact

```text
Clinical Fact
├── Symptom
├── Sign
├── Medication
├── Allergy
├── Procedure
├── Diagnosis
├── Family History
├── Social History
├── Vital Sign
├── Laboratory Result
├── Imaging Finding
├── Observation
├── Complaint
└── Assessment
```

As categorias são uma taxonomia de trabalho. A lista final e seus códigos
serão decididos depois da análise terminológica da Fase C.5.

## Modelo conceitual proposto

```text
ClinicalFact
├── id
├── type
├── category
├── value
├── unit
├── subject
├── patient
├── encounter
├── source
├── provenance
├── confidence
├── detected_at
├── updated_at
├── status
└── metadata
```

### Regras do modelo

1. `source` identifica quem ou o que originou o fato: Patient, Doctor, Speech,
   Medical NLP, FHIR, Lab, OCR, Wearable ou outro adapter aprovado.
2. `provenance` aponta para a cadeia rastreável: áudio, transcript, segmento,
   página, exame, dispositivo ou evento de origem.
3. `confidence` mede a confiança da extração/normalização, não a verdade
   clínica definitiva.
4. `subject`, `patient` e `encounter` delimitam o contexto clínico.
5. `value` pode ser textual, codificado, quantitativo ou temporal, sempre com
   `unit` quando aplicável.
6. Fact não conhece SOAP, FHIR, CID, prompt ou LLM.

## Lifecycle

```text
Detected
   ↓
Enriched
   ↓
Validated
   ↓
Updated
   ↓
Resolved
   ↓
Archived
```

`Updated` não significa sobrescrever o histórico. A proposta é manter uma
identidade lógica do fato com revisões imutáveis, permitindo reconstruir o que
foi observado em cada momento. O desenho exato de versionamento fica aberto
para os workshops seguintes.

## Provenance

```text
Audio
  ↓
Transcript
  ↓
Sentence / Segment
  ↓
Clinical Fact
  ↓
Clinical Reasoning
  ↓
Hypothesis / Recommendation
```

O consumidor deve conseguir responder: “de onde veio este fato?” sem depender
da representação final do documento.

## Dependências permitidas

```text
Clinical Fact
├── Clinical Reasoning pode ler
├── Medical Knowledge pode contextualizar
├── Clinical Representation pode projetar
├── Timeline pode registrar
└── Agent pode consumir
```

Clinical Fact não depende de SOAP, FHIR, Timeline, Knowledge Layer, ADK ou
qualquer provider específico.

## Decisões abertas para os próximos workshops

- O fato precisa de polaridade explícita (`present`, `absent`, `uncertain`)?
- `confidence` deve ser uma medida única ou separada em extraction/confidence e
  clinical certainty?
- Quando um fato importado de FHIR é validado pelo profissional?
- Como fatos contraditórios coexistem?
- Qual é a diferença formal entre `Assessment` como fato documentado e
  `Hypothesis` como raciocínio provisório?
- Quais categorias terão terminologias canônicas?

## Resultado do Workshop 1

**Proposed Decision:** Clinical Facts são o átomo de informação clínica do
Astera. A decisão só poderá ser marcada como `Approved` após a ADR-004 ser
avaliada pelo Astera Flow.
