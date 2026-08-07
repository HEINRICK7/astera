# ADR-001: Modular Monolith como Arquitetura Oficial do Astera

| Campo | Valor |
|---|---|
| **Status** | Aceito |
| **Data** | 2026-08-07 |
| **Decisor** | Astera Platform Team |
| **Categoria** | Arquitetura |

---

## Contexto

Durante o planejamento da Fase C (Core Platform), foi identificada uma ambiguidade na linguagem usada por Agentes de Engenharia que referiram-se à construção de "microsserviços". Essa linguagem contradiz a decisão arquitetural oficial do Astera Flow.

Antes de qualquer codificação da Fase C, esta decisão precisa ser formalizada como lei arquitetural.

---

## Decisão

O Astera será construído inicialmente como um **Modular Monolith**.

### Arquitetura Oficial

```
Modular Monolith
+ Hexagonal Architecture (Ports & Adapters)
+ Event Driven Architecture
+ Plugin First Design
+ Cloud First
+ Cloud Agnostic
```

### O que isso significa na prática

| Conceito | Correto ✅ | Incorreto ❌ |
|---|---|---|
| Unidade de deploy | Um único processo Python | Múltiplos serviços independentes |
| Comunicação interna | Events via NATS (in-process ou local) | HTTP entre serviços |
| Organização do código | Módulos dentro do monólito | Repositórios separados por serviço |
| Runtime | Um Astera Runtime central | Múltiplos runtimes |
| Banco de dados | Compartilhado com isolamento lógico | Um banco por serviço |
| Deploy inicial | `docker-compose up runtime` | Orquestração de N serviços |

---

## Rationale

### Por que Modular Monolith?

1. **Velocidade de desenvolvimento**: Um único processo é mais rápido de desenvolver, testar e iterar no estágio atual da plataforma.

2. **Complexidade controlada**: Microsserviços adicionam complexidade de rede, latência, descoberta de serviços e debugging distribuído antes que o produto seja validado.

3. **Plugin First como substituto de microsserviços**: A arquitetura Plugin First oferece os mesmos benefícios de extensibilidade sem a penalidade operacional de microsserviços no início.

4. **Caminho de extração preservado**: A Arquitetura Hexagonal (Ports & Adapters) garante que qualquer módulo possa ser extraído para um microsserviço independente no futuro, sem refatoração da lógica de domínio.

5. **Alinhamento com DDD**: Domain-Driven Design favorece bounded contexts bem definidos dentro de um monólito antes da extração.

### Por que não Microsserviços agora?

- Nenhum produto foi validado ainda.
- A equipe de engenharia ainda é pequena.
- A infraestrutura de service mesh, distributed tracing e API gateway ainda não está madura.
- Problemas de latência de rede entre serviços internos são desnecessários neste estágio.

---

## Consequências

### Positivas

- Desenvolvimento da Fase C significativamente mais simples.
- Um único `make run` sobe toda a plataforma.
- Debugging local sem necessidade de Docker para cada serviço.
- Testes de integração mais simples (sem mocks de rede entre serviços).
- Refatoração futura preservada pela Arquitetura Hexagonal.

### Negativas (aceitas conscientemente)

- Escala vertical limitada por processo único (aceitável no MVP).
- Deploy de um componente requer redeploy do monólito (aceitável no MVP).
- Times não podem fazer deploy independente por módulo (aceitável no MVP).

---

## Regra de Extração Futura

Um módulo **PODE** ser extraído para microsserviço quando:

1. O módulo tiver carga de trabalho mensurável que justifique escala independente.
2. O módulo tiver contrato estável (sem alterações de interface por 2+ sprints).
3. Um ADR específico for aprovado para a extração.
4. A infraestrutura de service mesh estiver disponível (Fase H ou posterior).

---

## Regra para Agentes

> Todo Agente que usar as palavras "microsserviço", "microservice", "serviço independente"
> ou "serviço separado" em referência a módulos internos do Astera está em violação desta ADR.
>
> A linguagem correta é: **módulo**, **bounded context**, **plugin**, **componente do Runtime**.

---

## Referências

- Astera Flow — Arquitetura Oficial v1.0
- Engineering Execution Plan v1.0
- `docs/architecture/` — Diagramas da Arquitetura Hexagonal
- [Building Microservices, Sam Newman] — Capítulo sobre quando NÃO usar microsserviços
- [Modular Monolith: A Primer, Kamil Grzybek]
