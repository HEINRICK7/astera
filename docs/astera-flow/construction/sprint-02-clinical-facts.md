# Construction Sprint 2 — Clinical Facts Plugin

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Módulo** | Clinical Facts Plugin |
| **Contrato** | `ClinicalFact` / `clinical.fact.detected` |
| **Entrada** | Resultado provider-neutral de Medical NLP |
| **Saída** | Clinical Fact candidates com provenance |

## Escopo aprovado

Implementar a unidade atômica definida na Cognitive Architecture. O plugin
não diagnostica, não cria hipóteses, não consulta Medical Knowledge e não gera
SOAP/FHIR.

Cada fact deve manter, quando disponível:

- identidade, category e value;
- subject/patient e encounter;
- source e provenance reconstruível;
- confidence separada de certainty;
- polarity e status;
- revisão temporal sem apagar o fato de origem.

## Fluxo

```text
NlpResult → ClinicalFactExtractor → ClinicalFactsBatch → Runtime/Event Bus
```

## Critérios de validação

- facts positivos, negados e incertos são representáveis;
- `encounter_id` é preservado em todo item;
- origem, offsets e provider podem ser reconstruídos;
- confidence inválida é rejeitada;
- a saída não contém hipótese, recomendação ou representação documental;
- lifecycle do plugin registra capability, provider e health.

## Próximo módulo

Context Builder — status `IN PROGRESS` no Astera Flow.
