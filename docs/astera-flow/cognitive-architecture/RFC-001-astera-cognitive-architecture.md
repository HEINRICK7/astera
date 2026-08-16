# RFC-001 — Astera Cognitive Architecture

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Versão** | 0.1.0 |
| **Domínio** | Astera Flow / Cognitive Architecture |
| **Origem** | Workshops 1–5 + Workshop 6 de validação |
| **ADR relacionada** | ADR-009 |
| **Implementação** | Não autorizada nesta versão |

## Resumo

Esta RFC transforma a proposta dos cinco workshops da Fase C.5 em uma
especificação normativa para representar, raciocinar e enriquecer estado
clínico. Ela define o Clinical Context como centro vivo, separa Clinical World
de Medical World e estabelece Specialists como transformadores de contexto.

## Linguagem normativa

As palavras **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** e **MAY** têm
sentido normativo. Nesta versão, são requisitos de especificação; não são
ainda autorização para criar classes, endpoints, plugins ou schemas.

## Escopo

Esta RFC cobre:

- Clinical Facts como unidade atômica;
- Clinical Context como estado temporal e relacional;
- Clinical Reasoning Loop e hipóteses concorrentes;
- Medical Knowledge Layer independente do paciente;
- Specialists e enriquecimento incremental;
- contratos cognitivos, eventos e cenários de validação;
- governança de revisão, ADR e Astera Flow.

Esta RFC não escolhe LLM, banco, vector store, SDK, provider, prompt ou
framework de execução.

## Modelo canônico

```text
Conversation
   ↓
Transcript / fontes
   ↓
Clinical Facts
   ↓
Clinical Context vN
   ↓
Clinical Reasoning Loop
   ↓
Hypotheses / Information Gaps
   ↓
Knowledge Queries
   ↓
Medical Knowledge Objects
   ↓
Clinical Context vN+1
   ↓
Clinical Representations
```

O Context é o objeto cognitivo vivo. Cada Specialist MUST preservar a
proveniência e produzir uma versão posterior; representações como SOAP, FHIR,
Timeline e Referral MUST permanecer derivadas.

## Domínios e responsabilidades

| Domínio | Responsabilidade |
|---|---|
| Clinical World | Estado específico do paciente, encounter e consulta |
| Medical World | Conhecimento externo, versionado e referenciável |
| Runtime | Versionamento, validação, coordenação e persistência autorizada |
| Specialists | Enriquecimentos de responsabilidade única |
| ADK | Coordenação do contexto, sem autoridade clínica própria |
| Astera Flow | Design Authority e decisão de avanço |

## Governança de agentes

- **Cognitive Architect:** converte workshop em especificação, diagramas,
  contratos e ADR.
- **Domain Reviewer:** verifica fronteiras, duplicações, responsabilidades e
  ambiguidades.
- **Medical Validator:** verifica se o modelo representa o raciocínio clínico
  em consultas reais.
- **Engineering Reviewer:** verifica implementabilidade, desacoplamento,
  contratos e eventos.
- **Executor:** implementa somente após ADR e Astera Flow autorizarem.

Cada revisão MUST deixar resultado rastreável. `Approved` significa aprovado
no papel correspondente; não significa autorização de implementação até que o
Astera Flow registre essa decisão.

## Critérios de conformidade

Uma versão da RFC é consistente quando:

1. todos os termos possuem definição única;
2. cada entidade tem dono e fronteira;
3. cada transformação possui contrato, evento e provenance;
4. o cenário ponta a ponta é executável conceitualmente;
5. Clinical World e Medical World não se misturam;
6. nenhum Specialist promove hipótese a fato sem validação;
7. as ADRs e o Astera Flow apontam para a mesma versão.

## Estado e próximos artefatos

Os documentos 01–09 são a decomposição normativa desta RFC. As decisões
foram aprovados pelo Astera Flow e entram em Construction sob a ADR-010.

Architecture Review, Clinical Simulation e Reality Review estão registradas em
[10 — Architecture Review](10-architecture-review.md),
[11 — Clinical Simulation](11-clinical-simulation.md) e
[12 — Reality Review](12-reality-review.md).
