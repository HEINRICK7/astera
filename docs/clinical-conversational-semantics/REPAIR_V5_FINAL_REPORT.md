# Repair V5 — Final Report

Status: **FAIL — HUMAN GATE obrigatório**  
Data: 2026-08-15  
Corpus: V6 oficial congelado  
Policy: `clinical-semantic-policy-v1.1`

## Resultado executivo

As seis fases do Repair V5 passaram seus gates direcionados e de regressão. A
execução integral final do V6, porém, não passou o quality gate policy-aligned.
O resolver deve parar neste checkpoint.

## Scores finais

| Métrica | Policy-aligned quality gate | RAW V6 histórico |
|---|---:|---:|
| `mention_exact_match` | 0.7275 | 0.8593 |
| `relation_exact_match` | 1.0000 | 1.0000 |
| `cross_mention_isolation` | 0.5912 | 0.7664 |
| `cross_segment_resolution` | 0.8629 | 0.6532 |
| `speaker_attribution` | 1.0000 | 1.0000 |
| `provenance` | 1.0000 | 1.0000 |
| `scope_accuracy` | 0.9988 | 0.9946 |
| `status` | 0.7305 | 0.4304 |

O quality gate exigia, entre outros, mention ≥ 0.90, relation ≥ 0.95,
cross-mention ≥ 0.95 e cross-segment ≥ 0.90. Portanto:

`policy_aligned_v6_score.hard_gate_passed = false`

## Authority metrics

```text
resolver_decisions_total       = 4092
resolver_decisions_preserved   = 4011
resolver_decisions_overwritten = 81
legacy_fallback_count          = 0
ambiguous_forced_resolution    = 0
```

Provenance permaneceu perfeita e não houve fallback legado silencioso nem
resolução forçada de ambiguidades.

## Estado das fases

- V5.1 Attribute Ownership: PASS;
- V5.2 Transition Ownership: PASS;
- V5.3 Status / Current Assertion Semantics: PASS no gate direcionado;
- V5.4 Negation & Mention Scope: PASS;
- V5.5 Temporality Ownership: PASS;
- V5.6 Relation Resolution residual: PASS;
- V6 final policy-aligned: **FAIL**.

Os gates locais não foram suficientes para satisfazer o caminho completo do V6;
o diagnóstico detalhado está em [V5_FAILURE_ANALYSIS.md](V5_FAILURE_ANALYSIS.md).

## Integridade e bloqueios

- checksum V6: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`;
- corpus V6: não alterado;
- policy v1.1: não alterada;
- Type B: 10 findings excluídos somente do quality gate, preservados no RAW;
- holdouts: `NOT_EXECUTED`;
- V7: `BLOCKED`;
- Shadow Integration: `BLOCKED`;
- Production: `BLOCKED`;
- provider externo/LLM: não introduzido.

Resultado bruto completo e reproduzível: [context-validation-v6-repair-v5-final-2026-08-15.json](../../labs/terminology_benchmark/results/context-validation-v6-repair-v5-final-2026-08-15.json).

## Decisão

**STOP. HUMAN GATE.** Não executar holdouts nem iniciar novo repair automático
até decisão explícita sobre os erros residuais de status, ownership de menções e
resolução cross-segment.
