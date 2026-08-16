# Workshop 4 — Medical Knowledge Layer

| Campo | Valor |
|---|---|
| **Fase** | C.5 — Cognitive Architecture |
| **Workshop** | 4 — Medical Knowledge Layer |
| **Status** | Proposed Decision |
| **ADR** | ADR-007 |
| **Pré-requisito** | Workshop 3 / ADR-006 Proposed |
| **Pergunta central** | O que é conhecimento médico e como ele entra no raciocínio? |

## Princípio de trabalho

O Astera possui dois mundos que não podem ser misturados:

```text
Clinical World                         Medical World
Paciente                               Diretrizes
Clinical Facts                         Protocolos
Clinical Context                       Doenças e sintomas
Hypotheses                             Medicamentos e interações
Information Gaps                       Exames e critérios
Timeline                               Scores e regras clínicas
Encounter                              CID · SNOMED CT · LOINC · RxNorm
                                       Literatura curada
```

O Clinical World responde:

> O que sabemos sobre este paciente neste momento?

O Medical World responde:

> O que a medicina sabe sobre este problema?

Um Clinical Fact nunca altera o conhecimento médico. Uma diretriz, por sua
vez, nunca se torna um fato do paciente apenas por ter sido consultada.

## Decisão proposta

O **Medical Knowledge Layer** será uma biblioteca externa, versionada,
proveniente e imutável em produção. Ele armazenará conhecimento estruturado,
não pacientes nem documentos como unidade principal.

```text
Clinical Facts
    ↓
Clinical Context
    ↓
Clinical Reasoning
    ↓
Clinical Hypothesis
    ↓
Knowledge Query
    ↓
Medical Knowledge Layer
    ↓
Evidence-Based Result
    ↓
Clinical Reasoning Loop
```

A consulta ao conhecimento nasce de uma hipótese ou de uma lacuna de
informação contextualizada. O fluxo não é `Transcript → RAG → Recommendation`.

## Knowledge Query

`Knowledge Query` é a pergunta estruturada que conecta uma hipótese a uma
necessidade de conhecimento médico.

```text
KnowledgeQuery
├── id
├── context_id
├── hypothesis_id
├── query_type: criteria | exams | treatment | interaction | contraindication |
│              protocol | terminology | reference
├── target_concept
├── jurisdiction
├── population
├── as_of
├── requested_evidence_level
└── provenance
```

Exemplos:

```text
Hipótese: Síndrome Coronariana Aguda
Query: protocolos aplicáveis, exames recomendados,
       contraindicações e referências vigentes

Hipótese: Pneumonia
Query: critérios CURB-65, exames, antibióticos e critérios de internação
```

O Query contém o contexto necessário para selecionar conhecimento aplicável,
mas não copia o Clinical Context para dentro do acervo médico.

## Knowledge Object

O acervo será consultado por objetos estruturados e rastreáveis, e não por
blocos de texto recuperados sem semântica.

```text
KnowledgeObject
├── id
├── object_type
├── subject_concept
├── claims
├── applicability
│   ├── jurisdiction
│   ├── population
│   └── clinical_setting
├── authority
├── evidence_level
├── effective_from
├── effective_to
├── source_reference
├── source_version
├── license
├── status: draft | published | superseded | withdrawn
└── provenance
```

Exemplos de `object_type`:

- `disease`;
- `symptom`;
- `clinical_guideline`;
- `protocol`;
- `drug`;
- `drug_interaction`;
- `contraindication`;
- `recommended_exam`;
- `laboratory_reference`;
- `imaging_criterion`;
- `clinical_score`;
- `clinical_rule`;
- `terminology_concept`;
- `literature_claim`.

Cada objeto precisa preservar autoridade, vigência, população, jurisdição,
nível de evidência, fonte, versão e licença. Um objeto sem proveniência não é
resultado clínico confiável.

## Ingestão e publicação

Nenhuma consulta ou agente escreve no Medical Knowledge Layer. A alimentação
ocorre offline por pipelines de curadoria:

```text
Guideline / Protocol / Literature / Terminology
    ↓
Acquisition and License Check
    ↓
Parsing
    ↓
Normalization
    ↓
Clinical Curation
    ↓
Knowledge Objects
    ↓
Validation and Provenance
    ↓
Immutable Knowledge Snapshot
    ↓
Published Indexes / Terminology Services
```

Uma atualização não modifica silenciosamente o passado. Ela publica uma nova
versão do snapshot:

```text
Knowledge v1 → Knowledge v2 → Knowledge v3
```

Toda resposta deve identificar a versão do conhecimento consultada. Um índice
ou mecanismo de recuperação é uma projeção operacional do snapshot, não a
fonte de verdade.

## Domínios e terminologias

| Domínio | Uso primário no Astera | Regra de fronteira |
|---|---|---|
| Guidelines e protocolos | Recomendações condicionais e fluxos clínicos | Sempre preservar autoridade, vigência, jurisdição e população |
| Doenças e sintomas | Conceitos e relações clínicas reutilizáveis | Não representam a presença do conceito em um paciente |
| Drugs e interações | Conhecimento farmacológico | Não prescrevem nem alteram o contexto automaticamente |
| Exames e critérios | Requisitos, critérios e interpretação de referência | Não substituem o resultado observado no paciente |
| Scores e regras | Cálculos e critérios publicados | Entradas vêm do Clinical Context; regra vem do Knowledge Layer |
| Literatura curada | Claims e referências | Exigir citação, versão e nível de evidência |
| Terminologias | Identificação, validação e mapeamento de conceitos | Nunca persistir código sem `system` e versão quando aplicável |

### Política inicial de terminologias

- **SNOMED CT:** representação clínica e conceitos clínicos, mediante licença e
  edição/jurisdição aplicáveis.
- **LOINC:** observações, exames e medições laboratoriais ou clínicas,
  respeitando a licença e a versão publicada.
- **RxNorm:** conceitos de medicamentos e relacionamentos farmacológicos,
  respeitando os termos de uso e a versão do release.
- **CID/ICD:** classificação e exportação estatística, administrativa ou de
  interoperabilidade; não é a representação clínica interna universal.
- **FHIR:** modelo de intercâmbio e infraestrutura de terminologia. `CodeSystem`,
  `ValueSet` e `ConceptMap` suportam identificação, seleção e tradução, mas
  FHIR não é, sozinho, o acervo de conhecimento médico.

O Clinical Fact pode carregar texto livre e códigos mapeados, mas a codificação
deve manter `system`, `code`, `display` quando válido, versão e provenance.
Mapeamento não deve apagar o conceito original nem transformar equivalência
administrativa em equivalência clínica.

## Papel do ADK

O Google ADK não é o motor do conhecimento nem a autoridade clínica. Ele atua
como mediador operacional entre os dois mundos:

```text
Clinical Context
    ↓
Detecta hipótese ou Information Gap relevante
    ↓
Formula Knowledge Query
    ↓
Consulta retriever / terminology service / knowledge provider
    ↓
Recebe Knowledge Objects e referências
    ↓
Retorna resultado proveniente ao Clinical Reasoning Loop
```

O ADK não grava objetos no acervo, não promove uma recomendação a fato e não
produz diagnóstico final. A recomendação é uma projeção contextualizada,
sempre ligada à hipótese, aos fatos de entrada e ao snapshot consultado.

## Limites arquiteturais

Medical Knowledge Layer não deve:

- armazenar Patient, Encounter, Clinical Fact, Clinical Context ou Timeline;
- ser alterado durante uma consulta;
- depender de transcript, prompt, LLM ou Google ADK para existir;
- tratar documento bruto, embedding ou índice vetorial como conhecimento final;
- emitir recomendação sem fonte, versão e aplicabilidade;
- esconder conflitos entre fontes ou diferenças de jurisdição;
- substituir revisão clínica humana ou decisão profissional.

## Referências primárias consultadas

- [HL7 FHIR R5 Terminology Service](https://www.hl7.org/fhir/terminology-service.html)
- [HL7 FHIR R5 Terminologies](https://hl7.org/fhir/terminologies.html)
- [SNOMED International — Get SNOMED CT](https://www.snomed.org/get-snomed)
- [LOINC License](https://loinc.org/license)
- [NLM — RxNorm Files](https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html)
- [WHO — International Classification of Diseases](https://www.who.int/standards/classifications/classification-of-diseases/international-classification-of-diseases)

## Resultado do Workshop 4

**Proposed Decision:** Medical Knowledge Layer é o segundo cérebro do Astera:
independente do Clinical World, alimentado offline por curadoria, publicado em
snapshots imutáveis e consultado por `Knowledge Query` originada de hipóteses.
O ADK medeia os dois mundos; não os mistura.

A decisão aguarda ADR-007 e aprovação explícita do Astera Flow. Nenhum contrato
de código ou pipeline de ingestão será criado nesta etapa conceitual.
