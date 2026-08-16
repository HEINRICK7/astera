# Construction Sprint 3 — Context Builder

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Módulo** | Context Builder |
| **Capability** | `cognitive.clinical_context` |
| **Entrada** | `ClinicalFactsBatch` |
| **Saída** | `ClinicalContext` versionado |

## Resultado

O Context Builder cria a molécula cognitiva a partir dos facts sem executar
reasoning. O `context_id` permanece estável no encounter; novas entradas
produzem `context_version` maior, preservam os facts anteriores e acrescentam
eventos de timeline.

Relacionamentos, hipóteses, information gaps, knowledge references e
recommendations permanecem coleções explícitas no contexto para os módulos
seguintes, sem preenchimento inventado pelo Builder.

## Validação registrada

- Context v1 criado com facts e timeline.
- Context v2 preserva o estado anterior e adiciona novo fact.
- Encounter divergente é rejeitado.
- Plugin registra capability, provider, health e lifecycle.
- Suíte completa preserva os testes existentes.

## Arquivos de referência

- `packages/clinical_context_sdk/models.py`
- `packages/clinical_context_sdk/protocol.py`
- `packages/clinical_context_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/clinical_context/plugin.py`
- `apps/runtime/tests/test_clinical_context_plugin.py`

## Próximo módulo

**Reasoning Plugin — PLANNED**, conforme a ordem da Construction e o Clinical
Reasoning Loop aprovado.
