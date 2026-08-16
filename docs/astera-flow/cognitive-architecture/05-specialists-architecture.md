# 05 — Specialists Architecture

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Workshop origem** | Workshop 5 — Specialists e Clinical Representation |
| **ADR** | ADR-008 |
| **Responsável** | Runtime / Astera Flow |

## Objetivo

Definir uma equipe de Specialists de responsabilidade única, em vez de um
agente gigante, usando o Clinical Context como contrato cognitivo vivo.

## Definições

- **Specialist:** componente de responsabilidade única.
- **Context Enrichment:** transformação versionada que adiciona ou relaciona
  informação sem apagar histórico.
- **Clinical Representation:** projeção derivada do Context.

## Arquitetura

```text
Conversation → Transcript → Facts Specialist
                              ↓
                       Clinical Context vN
                              ↓
Reasoning → Knowledge → Gap Detection → Medication
                              ↓
                       Clinical Context vN+1
                              ↓
                    Documentation projections
```

## Specialists

| Specialist | Responsabilidade |
|---|---|
| Speech | Áudio → Transcript; aquisição e provenance |
| Clinical Facts | Transcript/fontes → Assertions/Facts |
| Context | Facts → relações, timeline e contexto |
| Reasoning | Context → hipóteses, suporte, conflitos e gaps |
| Knowledge | Hipóteses → Queries, objetos e referências |
| Gap Detection | Context → lacunas e perguntas |
| Medication | Context + Knowledge → interações e contraindicações |
| Documentation | Context → SOAP/FHIR/Timeline/Referral/Summary |

## Exemplo

`Reasoning Specialist(Context v2)` produz `Context v3` com hipóteses; o
`Knowledge Specialist` recebe `Context v3` e produz `Context v4` com referências.

## Contrato normativo

Todo Specialist cognitivo após a criação do Context MUST receber `Context vN`
e devolver `Context vN+1` com `Specialist Invocation`, enrichments e
provenance. Specialists MUST NOT conversar diretamente nem persistir sem
validação do Runtime.

## ADK e Runtime

ADK MUST conhecer coordenação do Context, não SOAP, FHIR, PDF ou prontuário.
Runtime MUST controlar transições, versionamento, merge, revisão e publicação.
Specialist propõe; Runtime valida e registra.

## Eventos

`specialist.invocation.started`, `specialist.invocation.completed`,
`specialist.invocation.rejected`, `specialist.invocation.completed` e
`representation.manifest.created`.

## Validação e restrições

O pipeline deve provar que todos os Specialists usam o mesmo Context, que uma
hipótese não vira Fact, e que representações são regeneráveis. Nenhum
Specialist pode esconder fonte, certeza, temporalidade, status ou conflito.

## Questões abertas

Scheduler do loop, merge concorrente, retries, timeouts, revisão humana e
política de autorização são decisões de implementação posterior.
