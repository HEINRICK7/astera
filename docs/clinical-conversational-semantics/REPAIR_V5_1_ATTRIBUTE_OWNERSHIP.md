# Repair V5.1 — Attribute Ownership

Status: **PASS — fase concluída**  
Data: 2026-08-15  
Escopo: `TYPE_A_RESOLVER_ERROR` only

## Objetivo

Garantir que `experiencer` e `laterality` sejam atribuídos à menção clínica
correta, com owner e proveniência explícitos, sem alterar a semântica de
status, negação, temporalidade ou relações.

A decomposição causal desta fase contém 9 findings de ownership:

- 8 `WRONG_LATERALITY`;
- 1 `WRONG_EXPERIENCER`.

As 18 dependências downstream de resolução de relação não foram tratadas nesta
fase: 8 dependem de `ATTRIBUTE_OWNERSHIP` e 10 de `TRANSITION_OWNERSHIP`.

## Mudança implementada

O produtor local agora registra `attribute_ownership` para cada atributo
materializado, incluindo:

- `owner_mention_id`;
- `owner_span` quando a origem é local;
- `source_evidence_id` ou `owner_segment_id`;
- preservação do mapa no `ResolvedClinicalSemantics` autoritativo.

O resolver cross-segment usa a menção do segmento-alvo como owner. Isso torna
audível a regra de que atributos de duas menções não podem compartilhar
implicitamente o mesmo owner.

Arquivos de produção alterados:

- `labs/terminology_benchmark/context_safety.py`
- `labs/terminology_benchmark/cross_segment_context.py`

Testes adicionados em:

- `apps/runtime/tests/test_clinical_conversational_semantics.py`

## Gates

| Gate | Resultado |
|---|---:|
| Ownership de lateralidade nos 8 fixtures representativos | PASS |
| Ownership de experiencer familiar | PASS |
| Owner distinto para menções distintas | PASS |
| Proveniência de owner preservada | PASS |
| Testes de semântica conversacional | `22 passed` |
| Regressão do benchmark de terminologia | `18 passed` |
| `git diff --check` | PASS |
| Compilação dos módulos alterados | PASS |
| V6 completo | **DEFERRED** |

O valor semântico dos nove spans foi verificado por probes locais e pelo
adapter cross-segment. A avaliação integral do V6 não foi executada nesta fase,
conforme o gate de Repair V5.

## Proteções preservadas

- V6 corpus: congelado;
- checksum oficial: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`;
- policy semântica: v1.1 congelada;
- Type B: intocados;
- holdouts: `NOT_EXECUTED`;
- V7: `BLOCKED`;
- Shadow Integration: `BLOCKED`;
- Production: `BLOCKED`;
- provider externo/LLM: não introduzido.

## Decisão de fase

V5.1 passa o gate sintético, de invariantes, de proveniência e de regressão.
V5.2 — `Transition Ownership` pode iniciar. O V6 completo permanece reservado
para o encerramento do grupo causal/final do Repair V5.
