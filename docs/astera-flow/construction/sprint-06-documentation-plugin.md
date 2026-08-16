# Construction Sprint 6 — Documentation Plugin

| Campo | Valor |
|---|---|
| **Status** | Completed |
| **Módulo** | Documentation Plugin |
| **Capability** | `cognitive.representation` |
| **Entrada** | Knowledge record + Clinical Context provenance |
| **Saída** | SOAP, FHIR e Summary deriváveis |

## Resultado

O Documentation Plugin mantém as representações como projeções não canônicas e
agora carrega `context_id`, `context_version` e provenance no resultado. Isso
permite regenerar SOAP/FHIR/Summary sem transformar a representação em fonte do
raciocínio.

## Validação registrada

- SOAP, FHIR e Summary continuam disponíveis.
- A origem do Clinical Context é preservada no envelope de cada representação.
- A representação não cria hipótese ou Clinical Fact.
- Plugin registra capability, provider, health e lifecycle.

## Arquivos de referência

- `packages/representation_sdk/models.py`
- `packages/representation_sdk/in_memory.py`
- `apps/runtime/src/application/plugins/representation/plugin.py`
- `apps/runtime/tests/test_representation_plugin.py`

## Próximo módulo

**End-to-End Consultation — READY**, conforme a ordem oficial da Construction.
