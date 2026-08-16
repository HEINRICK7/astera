# 07 — Cognitive Events

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Escopo** | Vocabulário de eventos da Cognitive Architecture |
| **Dependências** | Documentos 01–06 |

## Objetivo

Definir eventos observáveis para reconstruir a evolução do Clinical Context e
desacoplar Specialists sem permitir comunicação direta entre eles.

## Catálogo normativo

| Evento | Emissor | Conteúdo mínimo |
|---|---|---|
| `clinical.fact.detected` | Facts Specialist | fact candidate + provenance |
| `clinical.fact.validated` | Runtime | fact + reviewer/status |
| `clinical.fact.enriched` | Context Specialist | fact + enrichment |
| `clinical.fact.updated` | Runtime | fact revision + reason |
| `clinical.fact.superseded` | Runtime | old/new fact ids |
| `clinical.fact.resolved` | Runtime | fact + resolution |
| `clinical.fact.archived` | Runtime | fact id + reason |
| `clinical.context.created` | Runtime | context id/version |
| `clinical.context.enriched` | Runtime | versions + enrichments |
| `clinical.context.conflict_detected` | Runtime | conflicting items |
| `clinical.context.completed` | Runtime/Medical Validation | context + validator |
| `clinical.context.archived` | Runtime | context + reason |
| `clinical.hypothesis.created` | Reasoning Specialist | hypothesis + support |
| `clinical.hypothesis.supported` | Reasoning/Medical Validation | hypothesis + evidence |
| `clinical.hypothesis.weakened` | Reasoning/Medical Validation | hypothesis + reason |
| `clinical.hypothesis.contradicted` | Reasoning/Medical Validation | hypothesis + conflict |
| `clinical.hypothesis.confirmed` | Medical Validation | hypothesis + validator |
| `clinical.hypothesis.rejected` | Medical Validation | hypothesis + reason |
| `clinical.hypothesis.closed` | Runtime | hypothesis + resolution |
| `clinical.information_gap.detected` | Reasoning/Gap Specialist | gap + question |
| `clinical.question.proposed` | Gap Detection Specialist | question + gap |
| `clinical.information_gap.resolved` | Runtime | gap + fact/evidence |
| `knowledge.snapshot.published` | Curation Pipeline | snapshot + version |
| `knowledge.query.created` | Knowledge Specialist | query + hypothesis/gap |
| `knowledge.object.retrieved` | Knowledge Specialist | object + snapshot |
| `knowledge.object.published` | Curation Pipeline | object + snapshot |
| `knowledge.object.superseded` | Curation Pipeline | old/new object ids |
| `knowledge.object.withdrawn` | Curation Pipeline | object + reason |
| `knowledge.reference.attached` | Knowledge Specialist | source + snapshot |
| `knowledge.source.superseded` | Curation Pipeline | old/new source versions |
| `clinical.recommendation.generated` | Reasoning/Knowledge Specialist | recommendation + references |
| `clinical.recommendation.revised` | Reasoning/Medical Validation | recommendation + reason |
| `clinical.recommendation.accepted` | Medical Validation | recommendation + validator |
| `clinical.recommendation.rejected` | Medical Validation | recommendation + reason |
| `clinical.recommendation.expired` | Runtime/Medical Validation | recommendation + reason |
| `specialist.invocation.started` | Runtime | specialist + input version |
| `specialist.invocation.completed` | Runtime | output version + provenance |
| `specialist.invocation.rejected` | Runtime | reason + input version |
| `representation.manifest.created` | Documentation Specialist | type + source context |
| `representation.reviewed` | Medical Validation | representation + validator |
| `representation.published` | Runtime/Medical Validation | representation + signature |
| `representation.archived` | Runtime | representation + reason |
| `medical.validation.requested` | Runtime | item + validation role |
| `medical.validation.started` | Medical Validator | item + validator |
| `medical.validation.completed` | Medical Validator | item + decision |

## Envelope

```json
{
  "event_id": "evt-123",
  "event_type": "clinical.context.enriched",
  "occurred_at": "2026-08-07T09:20:00-03:00",
  "aggregate_id": "ctx-1",
  "context_version": 2,
  "producer": "context-specialist",
  "payload": {},
  "provenance": {}
}
```

## Regras

Este é o vocabulário canônico. Os documentos MUST usar esses nomes; aliases
alternativos para versionamento de Context ou enriquecimento de Specialist não
devem ser criados para representar o mesmo fato.

Events MUST ser append-only para auditoria, idempotentes por `event_id`,
versionados e livres de credenciais ou prompts. Um evento não autoriza por si
só transição clínica; o Runtime e o workflow de revisão continuam soberanos.

## Validação

O cenário 08 deve reconstruir Context v1…vN apenas com eventos e provar que
uma rejeição ou conflito não apaga o item de origem.

## Questões abertas

Broker, retenção, ordering, replay, schema registry e segurança serão definidos
na especificação de infraestrutura, após aprovação arquitetural.
