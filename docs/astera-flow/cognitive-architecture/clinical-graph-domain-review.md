# Clinical Graph — Domain Review

| Campo | Valor |
|---|---|
| RFC | [RFC-002 — Clinical Graph Architecture](RFC-002-clinical-graph.md) |
| Status | Review pending |
| Gate | Antes do Sprint 2 — Clinical Context consumir Graph |
| Escopo | Modelagem clínica, sem integração de pipeline |

Esta revisão aprova o Sprint 1 como scaffold de modelagem, mas não aprova
Clinical Graph como dependência do CPI-001. O Graph é um modelo de domínio
canônico; não é banco de dados, índice ou decisão de adotar uma tecnologia de
persistência.

## 1. Catálogo de conceitos

### Nós clínicos candidatos

| Conceito | Decisão preliminar | Observação de domínio |
|---|---|---|
| Symptom | Node | Pode possuir duração, severidade, localização, gatilho e alívio |
| Condition | Node | Pode possuir tratamentos, observações e evidências |
| Medication | Node | Deve ser um item clínico, não apenas texto livre |
| Observation | Node | Inclui valor, unidade, interpretação e tempo |
| Allergy | Node | Deve preservar substância, reação e status |
| Procedure | Node | Ação clínica realizada ou planejada |
| Imaging | Subtipo candidato de Exam/Procedure | Validar distinção entre pedido, realização e resultado |
| Laboratory | Subtipo candidato de Exam/Procedure | Resultado deve ser Observation relacionada |
| Vaccination | Subtipo candidato de Procedure | Deve preservar produto, dose e data |
| Lifestyle | Node | Sono, alimentação, tabagismo, álcool e atividade |
| Risk Factor | Node ou papel semântico | Validar se é entidade própria ou relação com Condition/Observation |

### Conceitos que podem ser escopos, não nós

| Conceito | Hipótese para validação médica |
|---|---|
| Chief Complaint | Papel do Symptom/Condition dentro do Encounter |
| Review of Systems | Seção/coleção de Symptoms e Observations, com estado positivo/negativo |
| Family History | Escopo de proveniência familiar com pessoa, grau de parentesco e Condition |
| Social History | Escopo sobre Lifestyle e exposições, com temporalidade |
| Vital Signs | Observation tipada, não um nó genérico adicional |

Esses itens não devem ser implementados como novos nós antes da validação. A
distinção entre entidade, papel, seção e escopo evita inflar o catálogo.

## 2. Matriz de relacionamentos

| Origem | Relacionamento | Destino | Cardinalidade inicial | Estado |
|---|---|---|---|---|
| Symptom | HAS_DURATION | Observation/Attribute | 0..* | Scaffold |
| Symptom | HAS_SEVERITY | Observation/Attribute | 0..* | Scaffold |
| Symptom | HAS_LOCATION | Observation/Anatomy | 0..* | Scaffold |
| Symptom | HAS_TRIGGER | Observation/Factor | 0..* | Scaffold |
| Symptom | HAS_RELIEF | Observation/Factor | 0..* | Scaffold |
| Condition | HAS_MEDICATION | Medication | 0..* | Scaffold |
| Condition | HAS_OBSERVATION | Observation | 0..* | Proposto |
| Medication | HAS_DOSAGE | Observation/Attribute | 0..* | Scaffold |
| Medication | HAS_FREQUENCY | Observation/Attribute | 0..* | Scaffold |
| Medication | HAS_ROUTE | Observation/Attribute | 0..* | Proposto |
| Observation | HAS_EXAM | Exam/Procedure | 0..* | Proposto |
| Hypothesis | SUPPORTS | Fact/Graph Node | 0..* | Proposto |
| Hypothesis | CONFLICTS | Fact/Graph Node | 0..* | Proposto |

O scaffold atual só materializa relações derivadas de fatos na mesma ordem do
transcript. Isso é deliberadamente insuficiente para inferir relações clínicas
complexas; tais inferências precisam de regra explícita e validação médica.

## 3. Cardinalidade e identidade

- Uma Condition pode possuir zero, uma ou várias Medications.
- Uma Medication pode possuir múltiplas doses e frequências ao longo do tempo;
  uma alteração não deve sobrescrever a anterior.
- Um Symptom pode possuir múltiplas localizações, gatilhos, alívios e episódios.
- Uma Observation deve permitir múltiplos valores quando houver medições em
  tempos distintos.
- A cardinalidade padrão do Graph é `0..*`; restrições mais fortes exigem
  validação específica do tipo clínico.
- O `fact_id` permanece a âncora de proveniência; `node_id` não substitui a
  identidade do Fact.

## 4. Temporalidade

O modelo precisa distinguir pelo menos:

| Campo | Significado |
|---|---|
| `observed_at` | Quando o fato foi observado ou relatado |
| `valid_at` | Quando o fato é clinicamente válido |
| `recorded_at` | Quando o sistema registrou o fato |
| `effective_from/to` | Intervalo de validade de tratamento, condição ou exposição |
| `recurrence` | Episódio único, recorrente, contínuo ou desconhecido |

Exemplos obrigatórios para validação:

- Dor com duração de cinco dias não é igual a dor recorrente.
- Losartana usada hoje não é igual a Losartana usada há dois anos.
- Mudança de dose cria uma nova versão temporal, não mutação silenciosa.

O scaffold preserva `observed_at` e `valid_at` na proveniência do Node. Os
demais campos permanecem pendentes de decisão de domínio.

## 5. Proveniência mínima

Todo Node e toda Edge devem preservar, quando disponível:

```text
origin
  transcript
source_fact_id
source_ref
request_id
observed_at / valid_at
confidence
```

Uma Edge inferida deve declarar que foi construída a partir de Facts e não
apresentar a relação como se tivesse sido dita literalmente pelo paciente.
O Sprint 1 já expõe essa proveniência em Nodes e Edges.

## 6. Compatibilidade de projeções

| Consumidor | Entrada canônica | Regra |
|---|---|---|
| Clinical Context | Clinical Graph | Context não deve reconstruir relações a partir do transcript |
| Reasoning | Clinical Graph | Hipóteses devem apontar para Nodes/Facts de suporte |
| Knowledge | Query derivada do Graph | Consultas devem preservar hipótese, lacuna e proveniência |
| SOAP | Graph | Subjective/Objective/Assessment/Plan são projeções revisáveis |
| FHIR | Graph | Condition, Medication, Observation e Procedure devem ser mapeados com tempo e proveniência |

Nenhuma dessas integrações foi iniciada por esta revisão.

## 7. Golden Consultation 001 — desenho para validação médica

O desenho abaixo é uma representação de revisão, não uma decisão de UI ou
persistência:

```text
Encounter: Golden Consultation 001
│
├── Condition: Hipertensão
│   └── HAS_MEDICATION
│       └── Medication: Losartana
│           ├── HAS_DOSAGE: 50 mg
│           └── HAS_FREQUENCY: todas as manhãs
│
└── Symptom: Dor de cabeça
    ├── HAS_DURATION: cinco dias
    ├── HAS_LOCATION: testa
    ├── HAS_LOCATION: atrás dos olhos
    ├── HAS_SEVERITY: 8/10
    ├── HAS_TRIGGER: uso prolongado do computador
    └── HAS_RELIEF: ambiente escuro
```

Um médico deve conseguir confirmar se os agrupamentos, relações, negações e
tempos fazem sentido antes que o Graph seja usado por Context, Reasoning, SOAP
ou FHIR.

## Decisão da revisão

- [x] Sprint 1 aprovado como scaffold isolado.
- [ ] Catálogo de nós aprovado clinicamente.
- [ ] Matriz de relacionamentos aprovada.
- [ ] Cardinalidade aprovada.
- [ ] Temporalidade aprovada.
- [ ] Proveniência aprovada.
- [ ] Compatibilidade SOAP/FHIR aprovada.
- [ ] Golden Consultation 001 validada por médico.
- [ ] Sprint 2 autorizado.

O Sprint 2 permanece bloqueado até os itens pendentes serem revisados e
registrados no Astera Flow/ADR. Não alterar Kernel, ADK, Providers ou contratos
públicos durante esta revisão.
