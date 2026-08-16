# Repair V5.6 — Residual Relation Resolution

Status: **PASS — fase concluída**  
Data: 2026-08-15  
Escopo: relações residuais independentes de causas upstream

## Objetivo

Emitir `DISCONTINUED_AT` quando o status `discontinued` é resolvido no contexto
cross-segment. Relações de lateralidade e de transição não foram corrigidas
novamente: elas já estavam cobertas pelas fases de ownership correspondentes.

## Mudança implementada

Quando a resolução autoritativa produz `status=discontinued` e ainda não existe
relação equivalente, o materializador cria exatamente uma relação:

```text
source: context:<target-segment>
target: status
value: discontinued
relation: DISCONTINUED_AT
```

A relação preserva os segmentos que produziram a decisão de status e mantém
`source_mention_id` e `source` alinhados.

Arquivo de produção alterado:

- `labs/terminology_benchmark/cross_segment_context.py`

Teste adicionado em:

- `apps/runtime/tests/test_clinical_conversational_semantics.py`

## Casos de caracterização

- `losartana` — `parei na semana passada`;
- `enalapril` — `parei no mês passado`;
- `losartana` — `parei semana passada` com sintoma negado adjacente.

## Gates

| Gate | Resultado |
|---|---:|
| `DISCONTINUED_AT` emitida quando status é cross-segment | PASS |
| Source/target únicos | PASS |
| Proveniência do status preservada | PASS |
| Semântica conversacional + benchmark direcionado | `45 passed` |
| `git diff --check` | PASS |
| Compilação dos módulos alterados | PASS |
| V6 completo | **AUTHORIZED NOW** |

## Proteções preservadas

- V6 corpus/checksum: preservados;
- policy v1.1: congelada;
- Type B: intocados;
- holdouts: `NOT_EXECUTED`;
- V7, Shadow Integration e Production: `BLOCKED`;
- provider externo/LLM: não introduzido.

## Decisão de fase

V5.6 passa os gates e encerra o Repair V5. A única execução integral autorizada
agora é o V6 congelado, reportando `POLICY_ALIGNED_V6_SCORE` como quality gate e
`RAW_V6_SCORE` como métrica histórica.
