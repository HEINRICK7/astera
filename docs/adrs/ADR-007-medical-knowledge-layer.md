# ADR-007: Medical Knowledge Layer como segundo cérebro do Astera

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team |
| **Categoria** | Cognitive Architecture |
| **Workshop** | Workshop 4 — Medical Knowledge Layer |

## Contexto

Os Workshops 1 a 3 definiram o Clinical Fact, o Clinical Context e o Clinical
Reasoning Loop. O raciocínio precisa consultar medicina externa sem misturar
conhecimento geral com o estado temporal de um paciente.

O fluxo `Transcript → RAG → Recommendation` também não expressa a intenção
clínica. A consulta deve nascer de uma hipótese ou de um Information Gap e ser
executada contra conhecimento versionado e proveniente.

## Decisão

Adotar o **Medical Knowledge Layer** como segundo cérebro do Astera:

```text
Clinical World                         Medical World
Facts / Context / Hypotheses           Guidelines / Protocols / Terminologies
Gaps / Timeline / Encounter            Literature / Rules / Scores
```

O Medical Knowledge Layer:

1. armazena `Knowledge Objects`, não pacientes nem documentos brutos como
   unidade cognitiva;
2. recebe dados por pipelines offline de aquisição, licenciamento, parsing,
   normalização, curadoria e publicação;
3. publica snapshots imutáveis e identificáveis por versão;
4. é consultado por `Knowledge Query` vinculada a uma hipótese, contexto,
   jurisdição, população e data de vigência;
5. devolve resultados estruturados com fonte, autoridade, evidência,
   aplicabilidade e provenance;
6. não é escrito por agentes, consultas, pacientes ou ADK.

O ADK atua como mediador: observa o Clinical Context, formula a Knowledge
Query, coordena a consulta a providers/retrievers/terminology services e
devolve o resultado ao Clinical Reasoning Loop.

## Modelo conceitual

```text
ClinicalHypothesis
    ↓
KnowledgeQuery
    ├── hypothesis_id
    ├── target_concept
    ├── query_type
    ├── jurisdiction / population / as_of
    └── requested_evidence_level
    ↓
KnowledgeObject
    ├── subject / claims
    ├── authority / source_reference
    ├── evidence_level
    ├── effective_period
    ├── source_version / license
    └── applicability / provenance
    ↓
Evidence-Based Result
    ↓
Clinical Reasoning Loop
```

## Consequências esperadas

- Clinical Facts nunca alteram Medical Knowledge.
- Conhecimento médico deixa de depender da memória paramétrica do LLM.
- Uma recomendação pode ser reconstruída com a versão e as fontes consultadas.
- Mudanças de diretriz produzem uma nova versão, sem reescrever o passado.
- Terminologias ficam separadas de fatos e podem ser validadas, mapeadas ou
  exportadas de forma explícita.
- Retrieval, embeddings e bancos vetoriais tornam-se detalhes de projeção, não
  o contrato cognitivo do conhecimento.
- O ADK coordena a fronteira entre os dois mundos sem se tornar autoridade
  clínica.

## Limites

Esta ADR não escolhe banco vetorial, mecanismo de RAG, fornecedor de
terminologia, parser, formato de armazenamento ou política clínica específica.
Também não autoriza recomendações autônomas, prescrição ou promoção de
hipótese a diagnóstico.

## Governança e decisões pendentes

Esta ADR foi aprovada pelo Astera Flow. Permanecem como detalhes operacionais:

- hierarquia de evidência e conflitos entre fontes;
- política de atualização, retirada e reprodutibilidade de snapshots;
- processo de licenciamento por jurisdição e população;
- contrato de `Knowledge Query` e `Knowledge Object` em código;
- critérios de curadoria humana e validação clínica;
- composição de providers e terminology services.

Os contratos provider-neutral já estão implementados; adapters de produção
seguem a Construction sem alterar a arquitetura.

## Referências

- [Workshop 4 — Medical Knowledge Layer](../astera-flow/workshops/workshop-04-medical-knowledge-layer.md)
- [Workshop 3 — Clinical Reasoning Loop](../astera-flow/workshops/workshop-03-clinical-reasoning-loop.md)
- [ADR-005 — Clinical Context](ADR-005-clinical-context-as-cognitive-molecule.md)
- [ADR-006 — Clinical Reasoning Loop](ADR-006-clinical-reasoning-loop.md)
