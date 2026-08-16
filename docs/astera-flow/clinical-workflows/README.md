---
document_id: astera-clinical-workflow-certification
title: Clinical Workflow Certification
category: Product
status: Official
version: 1.1
owner: Astera Clinical Validation
depends_on:
  - ../product-backlog.md
  - clinical-workflow-dataset.md
used_by:
  - Product Engineering
  - Executive Dashboard
last_updated: 2026-08-07
---

# Clinical Workflow Certification

## Novo KPI

**Real Consultation Success Rate**: percentual de consultas que percorrem o
fluxo completo com áudio e providers reais, sem adaptação manual, desde Speech
até persistência clínica.

Este é o KPI de produto do Astera. O status de uma Capability continua sendo
útil para engenharia, mas não substitui a certificação de um workflow.

```text
Audio
  ↓
Speech
  ↓
Clinical Facts
  ↓
Clinical Context
  ↓
Reasoning
  ↓
Knowledge
  ↓
SOAP
  ↓
FHIR
  ↓
Persistence
```

## Capability Zero

O primeiro incremento de produto é o [CPI-001 — Primary Care Consultation](../product-backlog.md#cpi-001--primary-care-consultation).
Seu caso dourado está no [Clinical Workflow Dataset](clinical-workflow-dataset.md).

### Hipótese de produto

O CPI-001 não certifica faster-whisper, spaCy, Snowstorm ou HAPI FHIR
isoladamente. Ele verifica se o workflow de uma consulta clínica simples
funciona de ponta a ponta:

\`\`\`text
Audio → Transcript → Clinical Facts → Context → Reasoning → Knowledge
      → SOAP → FHIR → Persistence → Clinical Replay
\`\`\`

O resultado da sprint é uma decisão única: Yes, No ou Blocked.

| Etapa | Estado atual |
|---|---|
| Clinical Journey Executor | Implementado |
| Clinical Replay | Implementado em `ClinicalJourney` |
| Speech provider real | Pendente |
| Áudio clínico autorizado | Pendente |
| Cognitive pipeline completo | Harness validado com adapters determinísticos |
| FHIR gateway real | Pendente; gateway atual é in-memory |
| Persistência durável | Pendente |
| Real Consultation Success Rate | Não medido |
| Clinical Workflow Certification | Não emitida |

O harness existente prova a integração dos contratos, mas não é uma consulta
real. Nenhum status acima deve ser promovido até que áudio, Speech provider e
persistência real estejam disponíveis.

## Clinical Replay

Cada jornada salva etapas clínicas navegáveis:

```text
Encounter
  ├── Speech / Transcript
  ├── Clinical Facts
  ├── Clinical Context
  ├── Reasoning / Hypotheses
  ├── Knowledge Queries
  ├── SOAP
  ├── FHIR
  └── Persistence
```

O replay não aceita `ProviderTrace`, latência, retries, GPU ou diagnósticos. A
observabilidade permanece no evidence path.

## Clinical Workflow Certification

Um workflow só pode ser certificado quando todos os gates abaixo passarem no
mesmo caso clínico ou na mesma versão do Golden Clinical Dataset:

- Engineering;
- Speech real;
- Clinical Facts e Context;
- Reasoning e Knowledge;
- SOAP e FHIR;
- persistência;
- Medical Validation;
- CQA e Cognitive Regression.

Para o CPI-001, todos os gates precisam ser avaliados no mesmo caso. Um gate
verde de componente não pode compensar uma etapa ausente do workflow.

## Status por estágio

| Status | Significado |
|---|---|
| ✅ | Evidência suficiente no workflow e replay atual |
| 🟡 | Integrado, mas ainda aguardando validação ou evidência real |
| 🟢 | Saída gerada e revisável, sem equivaler a produção |
| ⚪ | Etapa ainda não executada ou sem evidência |

O dashboard usa esses estados para comunicar progresso clínico. Eles não devem
ser substituídos por percentuais de cobertura de código.

## Próxima evidência

Executar uma consulta autorizada com áudio real e provider real. Registrar o
Clinical Replay completo, medir perdas entre etapas e emitir o primeiro
`Real Consultation Success Rate`.
