# Astera Engineering Execution Plan v1.0

> Documento destinado exclusivamente aos Agentes de Engenharia.
>
> Este documento define a ordem oficial de construção da plataforma Astera.
>
> Nenhum Agent poderá iniciar uma fase antes da conclusão da anterior.
>
> Cada fase deverá atingir 100% de conclusão antes da próxima ser iniciada.
>
> A arquitetura oficial da plataforma encontra-se congelada na versão 1.0.
>
> Este documento torna-se a especificação executável da engenharia.

---

# Objetivo

Construir toda a plataforma Astera seguindo rigorosamente:

- Arquitetura Hexagonal
- Modular Monolith
- Event Driven
- Plugin First
- Cloud First
- Cloud Agnostic

Nenhum Agent poderá modificar a arquitetura.

Toda implementação deverá respeitar os documentos oficiais do Astera Flow.

---

# Regras Gerais

## REGRA 01

Nunca implementar funcionalidades fora da Sprint atual.

---

## REGRA 02

Nunca iniciar uma Sprint enquanto a anterior não estiver 100% concluída.

---

## REGRA 03

Todo código deve possuir testes.

---

## REGRA 04

Todo módulo deve possuir documentação.

---

## REGRA 05

Todo módulo deve possuir Health Check.

---

## REGRA 06

Todo módulo deve possuir observabilidade.

---

## REGRA 07

Toda comunicação interna utiliza NATS.

---

## REGRA 08

Nenhum módulo poderá acessar diretamente outro módulo.

Toda comunicação ocorre através de:

- Eventos
- Contratos
- Ports
- Adapters

---

## REGRA 09

Todo Plugin deverá utilizar o SDK oficial.

---

## REGRA 10

Nenhuma decisão arquitetural poderá ser alterada.

Caso seja necessário:

Criar ADR.

---

# Ordem Oficial

```
A

Bootstrap Platform

↓

B

Infrastructure

↓

C

Core Platform

↓

D

Cognitive Platform

↓

E

Clinical Platform

↓

F

Experience Layer

↓

G

Enterprise Platform

↓

H

Production

↓

I

MVP
```

---

# FASE A

Bootstrap Platform

Objetivo

Criar a fundação do projeto.

Criar

- Monorepo
- Estrutura de diretórios
- Docker
- Docker Compose
- Configuração
- CI
- Lint
- Testes
- Dev Containers

Critério

Projeto sobe completamente.

Nenhuma regra de negócio.

Definition of Done

- Build OK
- Docker OK
- Testes OK
- Health OK

---

# FASE B

Infrastructure

Criar

- PostgreSQL
- Redis
- Qdrant
- NATS
- MinIO
- Langfuse
- Grafana
- Prometheus
- Loki
- OpenTelemetry

Critério

Toda infraestrutura funcionando.

Todos os containers saudáveis.

Definition of Done

Todos os serviços respondem Health Check.

---

# FASE C

Core Platform

> ⚠️ ATENÇÃO ARQUITETURAL
>
> O Astera NÃO é uma arquitetura de microsserviços.
>
> A arquitetura oficial é: **Modular Monolith + Hexagonal Architecture + Event Driven + Plugin First**.
>
> Todo código da Fase C deve residir dentro do monólito modular.
>
> A extração para microsserviços é uma decisão futura e opcional.
>
> Referência: ADR-001 — Modular Monolith vs Microservices.

## Objetivo

Construir a fundação da plataforma Astera.

Um "Astera vazio, mas completamente operacional".

Nenhuma lógica clínica. Nenhum plugin cognitivo. Apenas a plataforma.

## Ordem Obrigatória

```
1
Astera Runtime
(domain / application / ports / adapters / infrastructure / bootstrap)

↓

2
Shared Kernel
(packages/shared — contratos internos, tipos base, utilitários)

↓

3
Event Bus SDK
(packages/shared/events — abstração NATS, publisher, subscriber)

↓

4
Configuration SDK
(packages/shared/config — loader, validação, env)

↓

5
Observability SDK
(packages/shared/observability — OTel, métricas, logs estruturados)

↓

6
Plugin SDK
(packages/plugin-sdk — interface, registry, lifecycle)

↓

7
API Oficial
(apps/api — FastAPI, rotas, middlewares, health)

↓

8
Primeiro Plugin (echo/ping)
(validação da cadeia completa Runtime → Plugin → API)
```

## Platform Bootstrap

O Runtime deverá inicializar nesta ordem exata:

```
Astera Runtime

↓

Application Startup

↓

Configuration Loader

↓

Dependency Container

↓

Event Bus

↓

Plugin Registry

↓

Health Manager

↓

Lifecycle Manager

↓

API Startup
```

## Estrutura do Runtime

```
apps/runtime/src/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   └── exceptions/
├── application/
│   ├── runtime/
│   ├── plugins/
│   ├── sessions/
│   ├── events/
│   ├── configuration/
│   └── health/
├── ports/
│   ├── inbound/
│   └── outbound/
├── adapters/
│   ├── http/
│   ├── nats/
│   └── persistence/
├── infrastructure/
│   ├── container/
│   ├── settings/
│   └── logging/
└── bootstrap/
    └── main.py
```

## Estrutura dos Packages

```
packages/
├── shared/
│   ├── contracts/
│   ├── events/
│   ├── sdk/
│   ├── config/
│   ├── observability/
│   └── security/
└── plugin-sdk/
```

## Proibições específicas desta Fase

- NÃO criar serviços independentes (sem microsserviços)
- NÃO implementar lógica clínica
- NÃO integrar Google ADK
- NÃO integrar Speech, OCR, Medical NLP
- NÃO criar funcionalidades de domínio médico

## Critério

Runtime inicializa corretamente.

Platform Bootstrap completo e operacional.

## Definition of Done

- `make run` sobe o Runtime sem erros
- Health Check responde em `/health`
- Event Bus conectado ao NATS
- Plugin Registry inicializado (sem plugins ainda)
- Configuration Loader carrega variáveis de ambiente
- Observability enviando traces para OTel
- Logs estruturados funcionando
- Testes unitários passando
- Testes de integração passando

---

# FASE D

Cognitive Platform

Criar

- Plugin System
- Google ADK
- Medical Knowledge Layer
- LiteLLM
- Open Source AI Modules

Ordem

1 Speech

2 Vision

3 OCR

4 Medical NLP

5 Terminology

6 FHIR

7 Embeddings

8 Evaluation

Cada módulo deve nascer como Plugin.

Critério

Primeiro agente cognitivo funcionando.

---

# FASE E

Clinical Platform

Criar pipeline clínico.

```
Speech

↓

Evidence

↓

Correlation

↓

Understanding

↓

Knowledge

↓

Representation
```

Critério

Primeiro SOAP funcionando.

---

# FASE F

Experience Layer

Criar

- Login
- Workspace
- Timeline
- Dashboard
- Encounter
- Patient
- Streaming
- A2UI

Critério

Primeira consulta visual.

---

# FASE G

Enterprise Platform

Criar

- Observabilidade
- Auditoria
- Segurança
- LGPD
- Backup
- Disaster Recovery
- Performance

Critério

Checklist Enterprise aprovado.

---

# FASE H

Production

Criar

- Kubernetes
- Helm
- AWS
- CI/CD
- Rollback
- Blue/Green

Critério

Primeiro Deploy.

---

# FASE I

Astera MVP

Objetivo

Entregar o primeiro fluxo clínico ponta a ponta.

Fluxo obrigatório

Login

↓

Paciente

↓

Novo Encounter

↓

Áudio

↓

Speech

↓

Evidence

↓

Knowledge

↓

SOAP

↓

Salvar

Critério

Consulta completa funcionando.

---

# Processo Obrigatório para Cada Sprint

Todo Agent deverá seguir exatamente esta sequência.

```
1

Ler documentação oficial

↓

2

Planejar implementação

↓

3

Criar Interfaces

↓

4

Criar Ports

↓

5

Criar Contracts

↓

6

Criar Eventos

↓

7

Implementar Casos de Uso

↓

8

Criar Adapters

↓

9

Criar Infraestrutura

↓

10

Criar Testes Unitários

↓

11

Criar Testes de Integração

↓

12

Adicionar Observabilidade

↓

13

Executar Health Check

↓

14

Atualizar Documentação

↓

15

Validar Critérios de Aceite

↓

16

Marcar Sprint como Concluída
```

---

# Checklist Obrigatório por Módulo

Cada módulo deverá entregar obrigatoriamente:

- Código
- Interfaces
- Ports
- Adapters
- Eventos
- Configuração
- Testes
- Observabilidade
- Docker
- Documentação
- ADR (quando necessário)

Nenhum módulo será considerado concluído sem esses itens.

---

# Critérios de Qualidade

Todo código deverá seguir:

- SOLID
- Clean Code
- Clean Architecture
- Arquitetura Hexagonal
- Modular Monolith
- Domain Driven Design
- Event Driven Architecture

---

# Proibições

Os Agents NÃO poderão:

- alterar arquitetura;
- criar dependências circulares;
- acessar banco diretamente entre módulos;
- ignorar Contracts;
- criar código duplicado;
- criar lógica fora do Runtime;
- comunicar módulos diretamente;
- quebrar compatibilidade.

---

# Definition of Done Global

A plataforma será considerada pronta quando:

✓ Todas as fases estiverem concluídas.

✓ Todos os testes passarem.

✓ Toda observabilidade estiver funcionando.

✓ Toda documentação estiver atualizada.

✓ Todos os módulos respeitarem a arquitetura oficial.

✓ O fluxo clínico completo estiver operacional.

---

# Missão dos Agents

Os Agents são responsáveis por transformar a arquitetura oficial do Astera em uma plataforma real.

Eles não possuem autonomia para alterar decisões arquiteturais.

Sua missão é implementar fielmente a arquitetura definida pelo Astera Flow, preservando qualidade, modularidade, testabilidade e evolução contínua da plataforma.

Este documento é a especificação executável oficial da engenharia do Astera.
