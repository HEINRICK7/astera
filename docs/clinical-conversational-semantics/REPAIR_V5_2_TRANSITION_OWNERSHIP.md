# Repair V5.2 — Transition Ownership

Status: **PASS — fase concluída**  
Data: 2026-08-15  
Escopo: `TYPE_A_RESOLVER_ERROR` only

## Objetivo

Separar explicitamente o atributo atual do atributo anterior em transições de
dose e frequência. A menção medicamentosa deve possuir o valor atual; o valor
anterior deve ser usado somente como origem de `CHANGED_FROM`.

Casos caracterizados:

- sertralina: `50 mg antes de dormir` → `75 mg pela manhã`;
- ibuprofeno: `200 mg se dor` → `400 mg a cada oito horas`;
- levotiroxina: `75 mcg em jejum` → `88 mcg antes do café`.

## Mudança implementada

- o vocabulário determinístico reconhece `a cada oito horas` e `antes do café`;
- a seleção de frequência privilegia o valor da etapa atual da transição;
- a relação `CHANGED_FROM` recebe o valor histórico correto;
- `transition_attribute_ownership` registra `current`, `previous`, owner da
  menção e segmento de origem;
- a proveniência da transição é preservada na `ResolvedClinicalSemantics` e na
  projeção autoritativa.

Arquivos de produção alterados:

- `labs/terminology_benchmark/context_safety.py`
- `labs/terminology_benchmark/cross_segment_context.py`

## Causalidade preservada

As relações downstream de transição não foram tratadas como causa independente.
Elas são geradas depois que o owner atual e o owner histórico estão definidos.
As dependências validadas para `TRANSITION_OWNERSHIP → RELATION_RESOLUTION`
permanecem representadas como downstream.

## Gates

| Gate | Resultado |
|---|---:|
| Dose atual nos 3 casos de transição | PASS |
| Frequência atual nos 3 casos de transição | PASS |
| `CHANGED_FROM` de dose | PASS |
| `CHANGED_FROM` de frequência | PASS |
| Proveniência de current/previous owner | PASS |
| Semântica conversacional + benchmark direcionado | `41 passed` |
| `git diff --check` | PASS |
| Compilação dos módulos alterados | PASS |
| V6 completo | **DEFERRED** |

## Proteções preservadas

- V6 corpus: congelado;
- policy semântica v1.1: congelada;
- Type B: intocados;
- holdouts: `NOT_EXECUTED`;
- V7, Shadow Integration e Production: `BLOCKED`;
- provider externo/LLM: não introduzido.

## Decisão de fase

V5.2 passa os gates sintético, de invariantes, de proveniência, de arquitetura
e de regressão. V5.3 — `Status / Current Assertion Semantics` pode iniciar.
