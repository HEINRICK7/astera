# Clinical Consultation Graph — Medical Domain Review

| Campo | Valor |
|---|---|
| RFC | RFC-002 — Clinical Graph Architecture |
| Review | Medical Domain Review |
| Status | Pending clinical validation |
| Decision | Sprint 1 approved; Sprint 2 blocked |
| Scope | Semântica clínica e representação da consulta |

Esta revisão não é uma revisão técnica. Ela não aprova implementação de
Context, Reasoning, Knowledge, SOAP ou FHIR. Seu objetivo é decidir se o Graph
representa uma consulta clínica real antes de se tornar a representação
canônica do domínio.

## 1. Chief Complaint

Pergunta: “Estou com dor de cabeça” é apenas um Symptom ou uma queixa
principal?

Decisão preliminar: `ChiefComplaint` deve ser tratado como um papel clínico
explícito no Encounter, ligado a um ou mais `Symptom`/`Condition`. A revisão
deve decidir se esse papel será um Node próprio ou uma relação tipada, sem
duplicar a entidade clínica.

Critérios:

- cardinalidade de uma ou mais queixas principais por Encounter;
- prioridade e ordem preservadas;
- ligação obrigatória a Fact(s) de origem;
- não confundir queixa principal com diagnóstico.

## 2. Review of Systems

Sintomas negativos são informação clínica, não ausência de informação.

Exemplos: “nega febre”, “nega perda de força” e “nega alergias”.

Decisão preliminar: `ReviewOfSystems` deve ser um escopo/seção do Encounter,
com Symptoms e Observations que preservem `polarity=negative`, `certainty` e
proveniência. A revisão deve decidir se será necessário um relacionamento
explícito `NEGATES` ou se a polaridade no Fact/Node é suficiente.

## 3. Family History

“Pai diabético” não é uma Condition do paciente.

Decisão preliminar: Family History precisa preservar:

- condição observada;
- pessoa ou grupo familiar;
- grau de parentesco;
- status temporal;
- origem e confiança.

Não deve ser representada como uma Condition sem escopo de sujeito, pois isso
contaminaria Context e Reasoning do paciente.

## 4. Social History

Social History deve agrupar Lifestyle, comportamento e exposições sem perder a
temporalidade.

Exemplos: tabagismo, álcool, sono, alimentação, atividade física e exposição
ocupacional.

Decisão preliminar: `SocialHistory` é um escopo clínico; `Lifestyle` e
`Behavior` são entidades/valores relacionados a esse escopo. “Não fuma” deve
continuar sendo um Fact negativo explícito.

## 5. Vital Signs

Vital Signs são `Observation` tipadas, não texto livre.

O modelo deve conseguir distinguir:

```text
PA: 140/90 mmHg
FC: 88 bpm
Temperatura: 37.2 °C
SatO2: 98 %
Peso: 72 kg
IMC: 25.4 kg/m²
```

Cada medição precisa de valor, unidade, timestamp, método quando aplicável,
proveniência e relação com o Encounter/Episode.

## 6. Episode

Episode é necessário para não confundir continuidade clínica com repetição de
texto.

Perguntas para validação:

- dor há cinco dias é um episódio atual;
- a mesma dor em um retorno após quinze dias continua no mesmo episódio ou
  cria um novo episódio relacionado;
- mudança de intensidade, tratamento ou diagnóstico cria versão ou novo
  episódio;
- Medication iniciada, suspensa ou alterada preserva histórico.

Decisão preliminar: Nodes clínicos não devem ser sobrescritos. O Graph precisa
de identidade de Episode e intervalos de validade antes de Context consumir
seus objetos.

## 7. Evidence e Proveniência

Cada Node e Edge deve responder “por que existe?”. O mínimo esperado é:

```text
origin: transcript | record | clinician | inference
source_fact_id
source_ref: segmento/linha/documento
request_id
observed_at
valid_at
confidence
```

Uma Edge inferida deve declarar que é inferida. Ela nunca pode parecer uma
afirmação literal do paciente.

O Sprint 1 já preserva essa estrutura básica; a validação médica deve confirmar
se `source_ref` e confiança são suficientes para auditoria e revisão.

## 8. Clinical Identity

Teste de identidade clínica:

1. Construir o Graph a partir dos Clinical Facts.
2. Remover o Transcript bruto.
3. Inspecionar somente Nodes, Edges, temporalidade e proveniência.
4. Perguntar: “o Graph ainda explica a consulta?”

O Graph deve explicar os sintomas, condições, tratamentos, negativos,
temporalidade e relações sem depender do texto original para reconstruir o
significado. O Transcript deve permanecer como evidência de origem, não como
dependência semântica.

## Catálogo para validação

| Grupo | Conceitos |
|---|---|
| Entidades clínicas | Symptom, Condition, Medication, Allergy, Procedure |
| Medições e resultados | Observation, Vital Sign, Laboratory, Imaging |
| Escopos clínicos | Chief Complaint, Review of Systems, Family History, Social History |
| Temporalidade | Episode, intervalos, recorrência, versões |
| Contexto | Lifestyle, Risk Factor, Vaccination |

A revisão deve decidir quais itens são Nodes, quais são escopos e quais são
papéis ou tipos especializados. Nenhum item desta tabela está automaticamente
aprovado para implementação.

## Nomenclatura

Recomendação: `Clinical Consultation Graph`.

`Clinical Knowledge Graph` pode ser confundido com o Medical Knowledge Layer,
que representa conhecimento médico externo e versionado. `Clinical Graph` é
genérico demais. A decisão final de renomear deve ocorrer antes de o Graph ser
promovido a representação canônica.

## Validação com consultas reais

Golden Consultation 001 é necessária, mas não suficiente. A validação médica
deve incluir pelo menos:

- atenção primária com sintoma e medicação;
- sintomas negativos em Review of Systems;
- histórico familiar e social;
- sinais vitais e resultados;
- retorno com mudança temporal;
- consulta pediátrica ou outro caso com sujeito/escopo distinto.

O Workbench poderá receber uma visualização de grafo após a aprovação do
modelo. Essa visualização deve mostrar Nodes, Edges, tempo e evidência, não
apenas JSON e não uma decisão de usar Neo4j.

## Decisão da Medical Domain Review

- [x] Sprint 1 — scaffold de modelagem aprovado.
- [ ] Chief Complaint validado.
- [ ] Review of Systems e negativos validados.
- [ ] Family History validado.
- [ ] Social History validado.
- [ ] Vital Signs validados.
- [ ] Episode e temporalidade validados.
- [ ] Evidence/proveniência validada.
- [ ] Clinical Identity validada sem Transcript bruto.
- [ ] Nomenclatura aprovada.
- [ ] Casos clínicos além da Golden Consultation 001 validados.
- [ ] Sprint 2 autorizado.

**Resultado:** Sprint 2 permanece bloqueado. O Clinical Graph ainda não é
declarado `Canonical Clinical Representation` até que um profissional clínico
valide esta revisão e a decisão seja registrada no Astera Flow/ADR.
