# Repair V5 Failure Analysis

Status: **HUMAN GATE**  
Data: 2026-08-15

## Evidência

O V6 final foi executado uma única vez sobre o corpus oficial congelado. O
quality gate policy-aligned falhou:

```text
mention_exact_match       0.7275   FAIL
relation_exact_match      1.0000   PASS
cross_mention_isolation   0.5912   FAIL
cross_segment_resolution  0.8629   FAIL
provenance                1.0000   PASS
```

Os dez findings Type B foram excluídos somente no nível dos campos do quality
gate. O RAW V6 permanece disponível para comparabilidade histórica.

## Diagnóstico causal atual

1. Relações não são mais o gargalo dominante: `relation_exact_match=1.0000`.
2. Provenance e autoridade de projeção permanecem íntegras.
3. `status` continua baixo mesmo no score policy-aligned (`0.7305`), indicando
   que o default de assertion status ainda não cobre o caminho completo do V6.
4. `cross_mention_isolation=0.5912` mostra que decisões de uma menção ainda
   estão divergindo em relação a menções irmãs, mesmo com os gates isolados de
   ownership, escopo e temporalidade passando.
5. `cross_segment_resolution=0.8629` melhorou, mas permanece abaixo de 0.90.

A conclusão segura é que o repair em fases reduziu os erros de relação e
preservou a arquitetura, mas não fechou a materialização semântica completa
das menções no harness V6. Não há evidência nesta execução para introduzir LLM,
MedGemma ou provider externo.

## Não fazer

- não executar holdouts;
- não criar V7;
- não iniciar Shadow Integration;
- não promover para Production;
- não alterar V6, gold ou policy;
- não iniciar outro repair automático sem nova decisão humana.

## Snapshot preservado

- checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`;
- Type B: 10, intactos;
- `legacy_fallback_count=0`;
- `ambiguous_forced_resolution_count=0`;
- holdouts: `NOT_EXECUTED`.

## Próximo gate

O próximo passo deve ser uma decisão humana sobre a decomposição dos 124 Type A
após o V5 final — especialmente status residual, isolamento entre menções e
cross-segment resolution. Nenhum código adicional está autorizado por este
relatório.
