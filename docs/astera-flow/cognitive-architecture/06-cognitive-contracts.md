# 06 — Cognitive Contracts

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Escopo** | Contratos entre Context, Specialists, Knowledge e Representations |
| **Dependências** | Documentos 01–05 |

## Objetivo

Consolidar os contratos normativos que conectam entidades sem acoplar a
implementação, provider ou formato de apresentação.

## Context Contract

```text
ClinicalContext
├── context_id / context_version
├── patient / encounter
├── facts / relationships / timeline
├── hypotheses / information_gaps
├── knowledge_references / recommendations
└── provenance / metadata
```

## Specialist Invocation Contract

```json
{
  "invocation_id": "inv-123",
  "specialist": "reasoning",
  "context_id": "ctx-1",
  "input_context_version": 4,
  "output_context_version": 5,
  "enrichments": [],
  "provenance": {}
}
```

## Knowledge Query Contract

Query MUST apontar hipótese ou gap, tipo de pergunta, conceito-alvo,
jurisdição, população, data e nível de evidência requerido.

## Representation Contract

SOAP/FHIR/Timeline/Referral/Summary MUST informar tipo, contexto de origem,
versão, itens incluídos, omissões justificadas, status e provenance.

## Recommendation Contract

Uma Recommendation MUST apontar para a hipótese/contexto que a originou,
Knowledge References, nível de certeza, status e revisão necessária. Ela é uma
proposta de raciocínio; não é prescrição, diagnóstico ou Clinical Fact.

```text
ClinicalRecommendation
├── id / context_id / hypothesis_id
├── action_or_statement
├── rationale / knowledge_references
├── status: proposed | reviewed | accepted | rejected
└── provenance / reviewer
```

## Invariantes

1. `output_context_version > input_context_version`.
2. Todo item tem origem e temporalidade, diretamente ou por envelope.
3. Hipótese não é fato; recomendação não é prescrição.
4. Knowledge Reference identifica snapshot e fonte.
5. Representação não é fonte canônica do raciocínio.

## Eventos relacionados

Todo contrato MUST indicar evento de criação, atualização, rejeição e conclusão
quando aplicável. O catálogo normativo está no documento 07.

## Validação

Contratos devem ser testados conceitualmente no cenário 08 e revisados pelos
Domain, Clinical e Engineering Reviewers antes de ADR.

## Questões abertas

Schema físico, serialização, compatibilidade de versões e política de erro
ficam fora desta RFC e serão decididos após aprovação.
