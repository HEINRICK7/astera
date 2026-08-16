# Cognitive Architecture — Research Notes

## Objetivo da pesquisa

Pesquisar como padrões clínicos e de interoperabilidade separam observações,
evidência, conhecimento, raciocínio e representação. As fontes abaixo são
referências de estudo; não são decisões de arquitetura do Astera.

## Achados principais

| Tema | Achado | Implicação para o Astera |
|---|---|---|
| FHIR Clinical Reasoning | O módulo representa, distribui e avalia artefatos como regras CDS, protocolos, medidas de qualidade e resumos de evidência | Knowledge deve ser versionado e separável do estado individual do paciente |
| FHIR Evidence | `Evidence` expressa variáveis, estatísticas e certeza de uma evidência; é uma unidade de evidência científica, não um sinônimo automático de fala do paciente | O modelo interno de evidência clínica precisa distinguir evidência observacional de evidência científica reutilizada |
| FHIR EvidenceVariable | Descreve aquilo sobre o qual o conhecimento/evidência trata, incluindo estruturas como população, exposição e resultado | Hipóteses e consultas de conhecimento podem carregar variáveis explícitas |
| SNOMED CT | Terminologia clínica lógica, hierárquica e polissêmica para significados clínicos | Terminologia de conceitos/fatos, com provenance e contexto fora do código do conceito |
| LOINC | Identifica observações, medições, exames e documentos | Medidas e resultados devem ter uma camada semântica própria, sem usar SNOMED para tudo |
| RxNorm | Normaliza nomes e identificadores de medicamentos e media vocabulários farmacêuticos | Medicamentos e interação medicamentosa devem ser um domínio de Knowledge distinto |
| OpenMRS | Usa um concept dictionary como base de formulários, observações, pedidos e resumos | A camada de conceitos precisa ser governada, versionada e reutilizável |
| Clinical reasoning research | A literatura descreve geração/modificação de hipóteses e raciocínio hipotético-dedutivo, indutivo, abdutivo e baseado em regras | Hipothesis não é fato; seu estado e justificativa precisam ser rastreáveis |
| Ambient documentation | Produtos do mercado se concentram em conversa/transcrição/documento, com integração a workflow clínico | SOAP é uma representação derivada e revisável, não o armazenamento cognitivo primário |

## Separações que a Fase C.5 precisa preservar

### Transcript não é Evidence

Transcript é uma representação da conversa. Evidence é uma afirmação ou pacote
de suporte com origem e contexto. Uma mesma transcrição pode gerar várias
afirmações, e uma afirmação pode ter várias fontes.

### Clinical Fact não é Hypothesis

Fact é uma afirmação observada ou extraída sobre o paciente, com certeza e
proveniência. Hypothesis é uma interpretação provisória que explica um conjunto
de fatos/evidências e pode ser confirmada, enfraquecida ou rejeitada.

### Patient Knowledge não é Medical Knowledge

O estado do paciente é contextual e temporal. Medical Knowledge é externo,
versionado, jurisdicional e sujeito a autoridade/licença. A conexão entre os
dois deve ser explícita e auditável.

### Clinical Representation não é raciocínio

SOAP, FHIR e Timeline são projeções destinadas a consumo clínico,
interoperabilidade e histórico. Eles não devem ser a única fonte do raciocínio
nem apagar evidências e hipóteses que os originaram.

## Vocabulário de trabalho

| Termo | Definição provisória |
|---|---|
| **Conversation** | Interação clínica multimodal bruta |
| **Transcript** | Representação textual temporizada da conversa |
| **Clinical Assertion** | Afirmação candidata sobre paciente, evento ou estado |
| **Clinical Fact** | Assertion aceita como informação do caso, com provenance |
| **Evidence** | Suporte rastreável que aumenta ou reduz a força de uma afirmação/hipótese |
| **Clinical Context** | Estado temporal e situacional usado para interpretar o caso |
| **Knowledge** | Conteúdo médico externo, versionado e referenciável |
| **Hypothesis** | Explicação provisória construída a partir de fatos/evidências |
| **Information Gap** | O que falta descobrir para avaliar ou refinar uma hipótese |
| **Clinical Reasoning Loop** | Ciclo de observar, interpretar, formular hipóteses, perguntar e atualizar contexto |
| **Specialist** | Componente de responsabilidade única que recebe e enriquece o Clinical Context |
| **Context Enrichment** | Transformação versionada do Clinical Context sem apagar seu histórico |
| **Clinical Representation** | Projeção derivada do contexto, como SOAP, FHIR, Timeline, Referral ou Summary |
| **Medical Knowledge Layer** | Acervo externo, versionado e proveniente de conhecimento médico estruturado |
| **Knowledge Query** | Consulta estruturada, originada de hipótese ou lacuna, ao Medical Knowledge Layer |
| **Knowledge Object** | Unidade estruturada de conhecimento médico com autoridade, vigência, evidência, fonte e licença |
| **Clinical World** | Estado específico do paciente: facts, context, hypotheses, gaps, timeline e encounter |
| **Medical World** | Conhecimento independente do paciente: guidelines, protocolos, terminologias, literatura e regras |
| **Validation** | Processo de verificar consistência, suporte, contradição e revisão clínica |
| **Clinical Representation** | Projeção em SOAP, FHIR, Timeline ou outro formato consumidor |

## Decisões ainda abertas

1. A unidade canônica será `Clinical Assertion` ou outro conceito?
2. Evidence representará apenas suporte do caso ou também evidência científica?
3. Qual é o contrato mínimo de provenance e temporalidade?
4. Qual terminologia é fonte de verdade para cada domínio?
5. Quais transições exigem revisão/validação humana?
6. O agente pode gerar hipóteses sem recomendação, ou também propostas de ação?
7. Como contradições e versões são preservadas sem sobrescrever o histórico?

## Fontes primárias consultadas

- [HL7 FHIR Clinical Reasoning Module](https://fhir.hl7.org/fhir/clinicalreasoning-module.html)
- [HL7 FHIR R5 Evidence](https://hl7.org/fhir/R5/evidence.html)
- [HL7 FHIR R5 EvidenceVariable](https://hl7.org/fhir/R5/evidencevariable.html)
- [SNOMED CT Introduction](https://docs.snomed.org/snomed-ct-specifications/snomed-ct-editorial-guide/readme/snomed-ct-introduction)
- [LOINC — Get started](https://loinc.org/start)
- [NLM RxNorm Overview](https://www.nlm.nih.gov/research/umls/rxnorm/overview.html)
- [OpenMRS Concept Dictionary Basics](https://openmrs.atlassian.net/wiki/spaces/docs/pages/25475255/Concept%2BDictionary%2BBasics)
- [Five decades of research and theorization on clinical reasoning](https://pmc.ncbi.nlm.nih.gov/articles/PMC6717718/)
- [Nabla Core API — Introduction](https://docs.nabla.com/2026-02-20/guides/intro)
- [Microsoft Dragon Copilot documentation](https://learn.microsoft.com/en-us/industry/healthcare/dragon-copilot/)
- [Abridge — Generative AI for Clinical Conversations](https://www.abridge.com/)

## Conclusão provisória

O primeiro workshop deve começar pela unidade de **Clinical Assertion**, mas a
decisão continua Proposed. A pesquisa sustenta uma arquitetura em camadas,
com provenance e separação entre estado do paciente, evidência científica,
terminologias, raciocínio e documento final.
