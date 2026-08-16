# Repair V5.4 — Negation & Mention Scope

Status: **PASS — fase concluída**  
Data: 2026-08-15  
Escopo: `TYPE_A_RESOLVER_ERROR` only

## Objetivo

Restringir a negação à menção que possui o cue explícito e encerrar o escopo
em uma nova asserção contrastiva. A negação não pode vazar para menções
introduzidas por `mas`, `só`, `refere` ou equivalente.

## Mudança implementada

- `não vomitou` e a forma `não` imediatamente anterior ao span são reconhecidos
  como negação local;
- listas negativas continuam agrupadas quando não há quebra de escopo;
- `só`, `refere`, `relata`, `apresenta`, `sente` e `mantém` encerram o escopo
  negativo iniciado na menção anterior;
- o adapter cross-segment continua propagando apenas a decisão da menção-alvo.

Arquivos de produção alterados:

- `labs/terminology_benchmark/context_safety.py`

Testes adicionados em:

- `apps/runtime/tests/test_clinical_conversational_semantics.py`

## Casos de caracterização

- `não vomitou` → negado;
- `não vomitou, mas teve enjoo` → `enjoo` não negado;
- `sem tontura, só fraqueza` → `fraqueza` não negada;
- `nega palpitação, refere cansaço e peso` → `cansaço` e `peso` não negados.

## Gates

| Gate | Resultado |
|---|---:|
| Negação local explícita | PASS |
| Isolamento em cláusula contrastiva | PASS |
| Isolamento em `só` | PASS |
| Isolamento em nova asserção (`refere`) | PASS |
| Semântica conversacional + benchmark direcionado | `43 passed` |
| `git diff --check` | PASS |
| Compilação dos módulos alterados | PASS |
| V6 completo | **DEFERRED** |

## Proteções preservadas

- V6 corpus/checksum: preservados;
- policy v1.1: congelada;
- Type B: intocados;
- holdouts: `NOT_EXECUTED`;
- V7, Shadow Integration e Production: `BLOCKED`;
- provider externo/LLM: não introduzido.

## Decisão de fase

V5.4 passa os gates sintético, de invariantes, de escopo e de regressão.
V5.5 — `Temporality Ownership` pode iniciar.
