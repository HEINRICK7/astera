# Repair V5.3 — Status / Current Assertion Semantics

Status: **PASS — fase concluída**  
Data: 2026-08-15  
Escopo: `TYPE_A_RESOLVER_ERROR` only

## Objetivo

Materializar o status de uma asserção clínica de acordo com a policy v1.1:

- asserção atual não negada → `status=present`;
- asserção histórica não negada → `status=historical`;
- asserção negada → `status=null`;
- status farmacológico continua sendo resolvido pelas regras específicas de
  medicação.

## Boundary de policy

Os corpora históricos V2–V5 registram `status=null` para parte das menções
positivas. Para evitar uma alteração retroativa silenciosa, a nova semântica é
ativada somente quando o contrato declara explicitamente:

`semantic_policy="clinical-semantic-policy-v1.1"`

O default permanece compatível com os corpora históricos. Não há seleção por
`case_id`, alteração de gold ou fallback oculto.

## Mudança implementada

- `ClinicalContextQuery` aceita a policy semântica declarada;
- o harness V6 declara a policy v1.1 explicitamente;
- o adapter cross-segment preserva a policy ao delegar ao produtor local;
- a regra de status exige uma asserção clínica explícita e não transfere status
  para menção negada ou experiencer familiar;
- `não tive` foi incluído no escopo determinístico de negação.

Arquivos de produção alterados:

- `apps/runtime/src/ports/outbound/clinical_semantics.py`
- `labs/terminology_benchmark/context_safety.py`
- `labs/terminology_benchmark/context_harness.py`
- `labs/terminology_benchmark/v6_harness.py`
- `labs/terminology_benchmark/cross_segment_context.py`

## Gates

| Gate | Resultado |
|---|---:|
| Current assertion → `present` | PASS |
| Historical assertion → `historical` | PASS |
| Negated assertion remains `null` | PASS |
| Legacy corpus compatibility | PASS |
| Semântica conversacional + benchmark direcionado | `42 passed` |
| `git diff --check` | PASS |
| Compilação dos módulos alterados | PASS |
| V6 completo | **DEFERRED** |

## Proteções preservadas

- V6 corpus e checksum: preservados;
- policy v1.1: congelada;
- Type B: intocados;
- holdouts: `NOT_EXECUTED`;
- V7, Shadow Integration e Production: `BLOCKED`;
- provider externo/LLM: não introduzido.

## Decisão de fase

V5.3 passa os gates sintético, de invariantes, de compatibilidade e de
regressão. V5.4 — `Negation & Mention Scope` pode iniciar.
