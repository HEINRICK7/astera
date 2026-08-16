# Construction Sprint 7 — End-to-End Consultation

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Módulo** | End-to-End Cognitive Consultation |
| **Fluxo** | Speech → Facts → Context → Reasoning → Knowledge → Documentation |
| **Validação** | pytest end-to-end determinístico |

## Resultado

O `CognitiveConsultationPipeline` orquestra os boundaries aprovados em uma
consulta completa. Transcript não é convertido diretamente em SOAP: passa por
Clinical Facts, Clinical Context, Reasoning e Knowledge antes de gerar
representações derivadas.

## Validação registrada

- Áudio gera Transcript provider-neutral.
- NLP gera Clinical Facts rastreáveis.
- Context Builder cria contexto versionado.
- Reasoning gera hipóteses e Information Gaps.
- Knowledge Query referencia hipótese/gap e retorna fonte versionada.
- SOAP/FHIR/Summary carregam a origem do Clinical Context.

## Arquivos de referência

- `apps/runtime/src/application/clinical/cognitive_consultation.py`
- `packages/clinical_pipeline_sdk/models.py`
- `apps/runtime/tests/test_cognitive_consultation_pipeline.py`

## Construction

Os sete sprints definidos pelo Astera Flow estão implementados e cobertos por
testes. A evolução seguinte permanece sujeita ao CQA e às regras da ADR-010.
