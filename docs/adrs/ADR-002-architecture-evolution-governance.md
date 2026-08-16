# ADR-002: Governança de Architecture Evolution

| Campo | Valor |
|---|---|
| **Status** | Aceito |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team |
| **Categoria** | Governança Arquitetural |
| **Escopo** | Kernel, Providers, Operações e Enterprise |

---

## Contexto

O crescimento do Astera precisa preservar um Kernel simples e evitar que ideias
futuras sejam implementadas apenas porque parecem úteis. Evoluções de escopo,
impacto e risco diferentes também não devem aparecer como uma lista linear sem
classificação.

## Decisão

Toda evolução arquitetural será registrada no [Kernel Evolution
Backlog](../astera-flow/kernel-evolution-backlog.md) em um dos quatro níveis:

1. **LEVEL 1 — Core Evolution:** mudanças no Kernel, Policy Engine,
   Capability Resolver e Execution Plan.
2. **LEVEL 2 — Provider Evolution:** Provider Health, Quality Profile e Cost
   Model.
3. **LEVEL 3 — Operational Evolution:** Auto Scaling, Load Balancer, Circuit
   Breaker, Retry e Rate Limit.
4. **LEVEL 4 — Enterprise Evolution:** Billing, Marketplace, Multi Tenant
   Avançado e Licensing.

Cada registro deve informar status, trigger, impacto, complexidade, risco,
prioridade e custo estimado de refatoração.

Os estados permitidos são:

`Proposed`, `Approved`, `Planned`, `In Progress`, `Implemented`, `Deprecated`
e `Rejected`.

Nenhuma evolução altera o código apenas por estar registrada como `Approved`.

## Processo obrigatório

```text
Trigger → ADR → Astera Flow → Implementação → Validação
```

O trigger torna a proposta elegível para análise. A ADR formaliza a decisão
arquitetural. O Astera Flow autoriza a execução. A implementação e sua
validação atualizam o backlog, o Engineering Journal e os contratos afetados.

## Consequências

### Positivas

- Mudanças de Kernel têm rastreabilidade antes do primeiro commit.
- Impacto, risco e custo ficam comparáveis entre evoluções.
- Ideias experimentais não contaminam a arquitetura estável.
- O Astera Flow continua sendo a autoridade sobre ordem e aprovação.

### Negativas aceitas

- Uma evolução relevante exige documentação adicional antes da implementação.
- O backlog terá estados intermediários explícitos, sem transformar esses
  estados em novos checkpoints de fase.

## Referências

- [Astera Flow README](../astera-flow/README.md)
- [Kernel Evolution Backlog](../astera-flow/kernel-evolution-backlog.md)
- [ADR-001 — Modular Monolith](ADR-001-modular-monolith-vs-microservices.md)
