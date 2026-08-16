# ADR-008: Specialists e Clinical Context como objeto de enriquecimento

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team |
| **Categoria** | Cognitive Architecture |
| **Workshop** | Workshop 5 — Specialists e Clinical Representation |

## Contexto

Os workshops anteriores separaram Clinical Fact, Clinical Context, hipóteses,
lacunas e Medical Knowledge. Ainda falta definir quem toma decisões, como o
Runtime coordena especialistas e como uma representação como SOAP ou FHIR
permanece derivada.

Transcript é útil como fonte de extração e auditoria, mas não contém sozinho
as relações, versões, hipóteses, lacunas e referências necessárias ao
raciocínio clínico.

## Decisão

Adotar uma arquitetura de **Specialists** de responsabilidade única, usando o
Clinical Context vivo como contrato cognitivo central.

Cada Specialist cognitivo recebe uma versão do Clinical Context e devolve uma
versão enriquecida do mesmo objeto. O Runtime coordena a sequência, valida a
transformação e registra a proveniência.

O contexto inclui:

- assertions/facts com fonte, temporalidade, polaridade, certeza, status e
  provenance;
- relações e timeline;
- hipóteses concorrentes e Information Gaps;
- Knowledge References e a versão do snapshot consultado;
- estado de enriquecimento e histórico de versões.

O resultado da invocação é um `Context Update`/`Specialist Invocation`, com
Specialist, versão de entrada, versão de saída, enriquecimentos e provenance.
Não existe comunicação cognitiva direta entre Specialists.

O ADK conhece apenas a coordenação do Clinical Context e do ciclo de
enriquecimento. SOAP, FHIR, Timeline, PDF e prontuário são responsabilidades
de projeção, não conceitos necessários ao núcleo do ADK.

O Specialist propõe. O Runtime valida, versiona e atualiza o Clinical Context.
Nenhuma hipótese, recomendação, pergunta ou representação pode virar
Clinical Fact, diagnóstico, prescrição ou decisão publicada por omissão ou
conversão implícita.

## Invariantes do contrato

```text
Specialist(Clinical Context version N)
        ↓
Context Enrichment
        ↓ Runtime validation
Clinical Context(version N+1)
```

Cada item deve manter `source`, `observed_at`/`valid_at`, `polarity`,
`certainty`, `status`, `provenance` e `context_version` de forma direta ou por
envelope comum.

SOAP, FHIR, Timeline, referral e summary são `Clinical Representation`: saídas
derivadas do contexto, com manifesto de origem, itens incluídos, omissões
justificadas, status e provenance. O Documentation Specialist registra a
projeção, mas não substitui o contexto canônico.

## Consequências esperadas

- Cada Specialist raciocina sobre o estado estruturado, e não sobre texto bruto
  como fonte única.
- Hipóteses e fatos permanecem semanticamente separados.
- O ciclo CRL pode retornar ao Runtime sem perder versão ou proveniência.
- Saídas SOAP/FHIR podem ser regeneradas e auditadas.
- Contradições, baixa certeza, gaps e contraindicações podem ser expostos de
  forma tipada.
- O contrato não fica acoplado a um LLM, prompt, Google ADK ou formato de
  apresentação.

## Limites

Esta ADR não define schema de banco, SDK, provider, modelo de LLM, prompt,
formato FHIR específico, UI ou política clínica de aprovação. Também não
autoriza Specialist, agente ou ADK a persistir diretamente no Clinical Context
sem a validação e versionamento do Runtime.

## Governança

Esta ADR foi aprovada pelo Astera Flow. Specialists usam o Clinical Context e
as representações preservam provenance conforme a Construction.

## Referências

- [Workshop 5 — Specialists e Clinical Representation](../astera-flow/workshops/workshop-05-agent-context-and-clinical-representation.md)
- [Workshop 4 — Medical Knowledge Layer](../astera-flow/workshops/workshop-04-medical-knowledge-layer.md)
- [Workshop 3 — Clinical Reasoning Loop](../astera-flow/workshops/workshop-03-clinical-reasoning-loop.md)
- [ADR-005 — Clinical Context](ADR-005-clinical-context-as-cognitive-molecule.md)
- [ADR-006 — Clinical Reasoning Loop](ADR-006-clinical-reasoning-loop.md)
- [ADR-007 — Medical Knowledge Layer](ADR-007-medical-knowledge-layer.md)
