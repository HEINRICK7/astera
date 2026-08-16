# ADR-004: Clinical Fact como unidade atômica de informação

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team |
| **Categoria** | Cognitive Architecture |
| **Workshop** | Workshop 1 — O Pipeline Cognitivo |

## Contexto

O Astera precisa distinguir linguagem, transcript, entidade extraída, fato do
paciente, evidência científica, conhecimento médico, hipótese e documento
clínico. Usar `Evidence` para todos esses conceitos cria ambiguidade com
Evidence-Based Medicine e com o recurso FHIR Evidence.

## Decisão

Adotar **Clinical Fact** como a menor unidade de informação clínica verificável,
contextualizada e rastreável da plataforma.

Um Clinical Fact terá, conceitualmente, identidade, tipo, categoria, valor,
subject, patient, encounter, source, provenance, confidence, timestamps,
status e metadata.

Clinical Fact não conhece SOAP, FHIR, CID, prompts, LLMs ou providers. SOAP,
FHIR, Timeline, Knowledge Layer e agentes são consumidores/projeções dos fatos.

## Separação semântica

- **Clinical Fact:** informação sobre o paciente, observada, informada, medida
  ou importada.
- **Clinical Evidence:** suporte para uma hipótese ou recomendação.
- **Medical Knowledge:** diretrizes, protocolos, literatura, terminologias e
  conhecimento externo versionado.
- **Clinical Reasoning:** interpretação dos fatos usando contexto e knowledge.
- **Hypothesis:** explicação provisória, confirmável ou rejeitável.

## Lifecycle proposto

`Detected → Enriched → Validated → Updated → Resolved → Archived`

Atualização não autoriza apagar o histórico; o mecanismo de revisão ainda será
definido na C.5.

## Status e governança

Esta ADR foi aprovada pelo Astera Flow. O `evidence_sdk` continua representando
Clinical Evidence; Clinical Facts possuem o SDK e a boundary próprios.

## Consequências esperadas

### Positivas

- A linguagem do domínio fica alinhada ao fato clínico observado.
- Raciocínio e recomendação deixam de ser confundidos com dado bruto.
- Representações SOAP/FHIR/Timeline podem ser projeções independentes.
- Provenance e confiança ficam no centro do modelo.

### Questões abertas

- Polaridade, certainty e revisão de fatos contraditórios.
- Taxonomia e terminologias canônicas por categoria.
- Fronteira entre Assessment documentado e Hypothesis provisória.

## Referências

- [Workshop 1 — Clinical Facts](../astera-flow/workshops/workshop-01-clinical-facts.md)
- [Fase C.5 — Cognitive Architecture](../astera-flow/cognitive-architecture-phase.md)
- [ADR-003 — Cognitive Architecture Workshops](ADR-003-cognitive-architecture-workshops.md)
- [FHIR R5 Evidence](https://hl7.org/fhir/R5/evidence.html)
