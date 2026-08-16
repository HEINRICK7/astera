# ADR-006: Clinical Reasoning Loop como núcleo cognitivo

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team |
| **Categoria** | Cognitive Architecture |
| **Workshop** | Workshop 3 — Clinical Reasoning Model |

## Contexto

Clinical Context não é uma resposta final. Um médico relaciona fatos,
considera hipóteses concorrentes, identifica lacunas e faz perguntas para
obter novos fatos. Um fluxo linear `Paciente → LLM → SOAP` não representa esse
processo.

## Decisão

Adotar o **Clinical Reasoning Loop (CRL)** como mecanismo conceitual central:

```text
Observe → Interpret → Hypothesize → Ask → Observe again
         → Update Context → Refine Hypotheses → repeat
```

O CRL produz e atualiza `Clinical Hypothesis` e `Information Gap`. A hipótese
mantém confidence, fatos de suporte, fatos ausentes, fatos conflitantes,
status e provenance. O gap descreve o que falta saber, como descobrir e qual
pergunta ou aquisição pode gerar o próximo fato.

## Consequências esperadas

- O Astera representa possibilidades, não apenas uma conclusão única.
- Perguntas são derivadas de lacunas do contexto.
- Agentes e ADK coordenam o loop em vez de gerar SOAP diretamente.
- SOAP, FHIR, Timeline e recomendações são projeções posteriores do estado
  construído.
- A evolução do raciocínio permanece auditável e revisável.

## Limites

Hipótese não é diagnóstico. Confidence não é certeza calibrada. Gap não é
ausência comprovada. Pergunta não é ordem médica. O CRL não autoriza decisão
clínica autônoma nem implementação de algoritmos antes da aprovação do Flow.

## Governança

Esta ADR foi aprovada pelo Astera Flow. Os contratos de Clinical Hypothesis,
Information Gap e CRL estão implementados no `reasoning_sdk`.

## Referências

- [Workshop 3 — Clinical Reasoning Loop](../astera-flow/workshops/workshop-03-clinical-reasoning-loop.md)
- [Workshop 2 — Clinical Context](../astera-flow/workshops/workshop-02-clinical-context.md)
- [ADR-005 — Clinical Context](ADR-005-clinical-context-as-cognitive-molecule.md)
