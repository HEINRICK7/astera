# 04 — Medical Knowledge Layer

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Workshop origem** | Workshop 4 — Medical Knowledge Layer |
| **ADR** | ADR-007 |
| **Responsável** | Knowledge Specialist / Curators |

## Objetivo

Separar Clinical World de Medical World e definir conhecimento médico externo,
versionado, proveniente e independente do paciente.

## Definições

- **Medical World:** conhecimento externo e reutilizável da medicina.
- **Knowledge Query:** consulta originada de hipótese ou Information Gap.
- **Knowledge Object:** unidade estruturada com fonte, vigência, evidência e
  aplicabilidade.

## Entidades

```text
KnowledgeQuery
├── hypothesis_id / target_concept / query_type
├── jurisdiction / population / as_of
└── requested_evidence_level / provenance

KnowledgeObject
├── object_type / subject_concept / claims
├── authority / evidence_level / effective_period
├── source_reference / source_version / license
└── applicability / status / provenance
```

## Diagrama e exemplo

```text
Hypothesis → Knowledge Query → Knowledge Object → Context Reference
```

Uma query sobre Pneumonia pode retornar critérios, exames, protocolo e
referências vigentes sem registrar Pneumonia como fact do paciente.

## Contrato normativo

Knowledge Layer MUST ser alimentada offline por aquisição, licenciamento,
parsing, normalização, curadoria e publicação. Snapshots publicados MUST ser
imutáveis e identificáveis por versão. Consulta MUST nascer de hipótese ou
Information Gap contextualizado.

## Responsabilidades e eventos

Knowledge Specialist formula Query e enriquece Context com referências.
Pipelines de curadoria publicam snapshots. Eventos:
`knowledge.snapshot.published`, `knowledge.query.created`,
`knowledge.object.retrieved`, `knowledge.reference.attached` e
`knowledge.source.superseded`.

## Regras e restrições

1. Paciente, Encounter, Fact e Context nunca são persistidos no Knowledge Layer.
2. Agente, consulta e ADK não escrevem no acervo.
3. Documento bruto, embedding e índice não são Knowledge Object por si só.
4. Fonte, versão, vigência, autoridade, jurisdição e licença são rastreáveis.
5. Terminologias preservam `system`, `code` e versão quando aplicável.

## Validação

Uma query para Síndrome Coronariana deve retornar objetos estruturados,
referências e versão do snapshot, sem criar diagnóstico nem alterar facts.

## Questões abertas

Hierarquia de evidência, conflitos entre fontes, curadoria clínica, licenças e
providers permanecem decisões de governança.
