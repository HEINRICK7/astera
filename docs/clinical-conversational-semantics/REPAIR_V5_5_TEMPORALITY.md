# Repair V5.5 — Temporality Ownership

Status: **PASS — fase concluída**  
Data: 2026-08-15  
Escopo: `TYPE_A_RESOLVER_ERROR` only

## Objetivo

A temporalidade deve pertencer ao evento ou menção que contém o cue temporal.
Um evento passado não pode transferir `past` para uma menção atual posterior,
e uma menção atual não pode apagar a temporalidade histórica do evento.

## Mudança implementada

- `há anos` e `há N anos` são reconhecidos como passado;
- o marcador de anos é avaliado no contexto local da menção-alvo;
- `conviveu` é reconhecido como cue histórico;
- cláusulas introduzidas por `mas`/`enquanto` mantêm ownership temporal
  independente;
- o status v1.1 usa a temporalidade já resolvida da menção correta.

Arquivo de produção alterado:

- `labs/terminology_benchmark/context_safety.py`

Testes adicionados em:

- `apps/runtime/tests/test_clinical_conversational_semantics.py`

## Casos de caracterização

- `Teve cirurgia no ombro há anos` → `past`;
- `hoje sente dormência no braço` → `current`;
- `O pai conviveu com hipertensão` → `past`;
- `a paciente nega pressão alta` → `current`.

## Gates

| Gate | Resultado |
|---|---:|
| Ownership de evento histórico | PASS |
| Isolamento de menção atual subsequente | PASS |
| Experiencer familiar sem transferência temporal | PASS |
| Semântica conversacional + benchmark direcionado | `44 passed` |
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

V5.5 passa os gates sintético, de ownership temporal e de regressão. V5.6 —
`Relation Resolution residual` pode iniciar, limitado às relações que não são
mais explicadas por ownership, transição, status, escopo ou temporalidade.
