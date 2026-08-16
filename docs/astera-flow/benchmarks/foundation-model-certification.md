# Foundation Model Certification

Foundation Model Certification avalia o modelo no runtime Google ADK. Ela não
certifica Capability Providers.

## Lifecycle

```text
Candidate
  ↓
Adapter Implemented
  ↓
Benchmark Passed
  ↓
Medical Validation Passed
  ↓
CQA Approved
  ↓
Foundation Model Approved
  ↓
Production Eligible
```

## Gates

| Gate | Evidência |
|---|---|
| ADK compatibility | adapter executa sem acoplamento ao Kernel |
| Benchmark | mesmo caso e mesmas Tools |
| Medical Validation | avaliação clínica autorizada |
| CQA | ausência de perda, invenção ou incoerência |
| Observability | modelo, adapter, request e métricas rastreáveis |
| Replaceability | troca sem alteração do ADK boundary ou domínio |

Nenhum Foundation Model recebe `Approved` ou `Production Eligible` com gate
ausente. A organização que instala o Astera escolhe o modelo de produção.
