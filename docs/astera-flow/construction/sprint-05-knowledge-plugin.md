# Construction Sprint 5 — Knowledge Plugin

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Módulo** | Knowledge Plugin |
| **Capabilities** | `cognitive.knowledge`, `cognitive.query` |
| **Entrada** | Understanding snapshot ou Knowledge Query |
| **Saída** | Knowledge record ou referências versionadas |

## Resultado

O Knowledge Plugin preserva a consolidação cognitiva existente e agora expõe a
query provider-neutral do Medical Knowledge Layer. Queries podem apontar para
uma hipótese e um Information Gap, carregar filtros de população/jurisdição e
retornar evidências com source, versão, título, trecho e score.

## Validação registrada

- Consolidação Understanding → Knowledge permanece compatível.
- Query ligada a hipótese/gap retorna fonte e versão rastreáveis.
- Capability registry registra `cognitive.knowledge` e `cognitive.query`.
- O retriever continua substituível pelo boundary do Medical Knowledge SDK.

## Arquivos de referência

- `packages/medical_knowledge_sdk/models.py`
- `apps/runtime/src/application/plugins/knowledge/plugin.py`
- `apps/runtime/tests/test_knowledge_plugin.py`

## Próximo módulo

**Documentation Plugin — READY**, conforme a ordem oficial da Construction.
