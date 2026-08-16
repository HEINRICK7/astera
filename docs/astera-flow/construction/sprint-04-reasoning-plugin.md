# Construction Sprint 4 — Reasoning Plugin

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Módulo** | Reasoning Plugin |
| **Capability** | `cognitive.reasoning` |
| **Entrada** | `ClinicalContext` |
| **Saída** | Hypotheses, Information Gaps e Questions |

## Resultado

O Reasoning Plugin implementa uma iteração do Clinical Reasoning Loop. Ele
recebe o contexto, produz hipóteses concorrentes, explicita facts ausentes e
gera perguntas rastreáveis a cada gap.

O adapter determinístico existe para contract tests e demonstração do fluxo;
não representa uma decisão clínica de produção nem transforma confidence em
probabilidade calibrada.

## Validação registrada

- Hipóteses concorrentes coexistem com status `candidate`.
- Supporting facts são referenciados por id.
- ECG e troponina aparecem como Information Gaps no cenário de dor torácica.
- Cada pergunta referencia exatamente um gap e uma hipótese.
- Plugin registra capability, provider, health e lifecycle.

## Arquivos de referência

- `packages/reasoning_sdk/models.py`
- `packages/reasoning_sdk/protocol.py`
- `packages/reasoning_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/reasoning/plugin.py`
- `apps/runtime/tests/test_reasoning_plugin.py`

## Próximo módulo

**Knowledge Plugin — READY**, conforme a ordem oficial da Construction.
