# Astera Kernel — Backlog de Evolução Arquitetural

## Current Architecture

| Campo | Estado |
|---|---|
| **Current Architecture** | Stable |
| **Current Version** | 1.0 |
| **Architecture Debt** | 0 |
| **Approved Evolutions** | 6 |
| **Implemented** | 0 |

> **Status do documento:** Aprovado como evolução planejada.
> A arquitetura base atual permanece estável. Este backlog não autoriza
> implementação automática: cada evolução precisa seguir o ciclo de governança
> registrado abaixo.

## Architecture Evolution

### Níveis de evolução

| Nível | Categoria | Escopo | Regra de impacto |
|---|---|---|---|
| **LEVEL 1** | **Core Evolution** | Kernel, Policy Engine, Capability Resolver, Execution Plan | Exige ADR antes de qualquer alteração no Kernel |
| **LEVEL 2** | **Provider Evolution** | Provider Health, Quality Profile, Cost Model | Melhora seleção, qualidade e operação de providers |
| **LEVEL 3** | **Operational Evolution** | Auto Scaling, Load Balancer, Circuit Breaker, Retry, Rate Limit | Altera comportamento operacional sem mudar o domínio clínico |
| **LEVEL 4** | **Enterprise Evolution** | Billing, Marketplace, Multi Tenant Avançado, Licensing | Adiciona capacidades comerciais e organizacionais |

### Estado arquitetural

Cada evolução deve usar exclusivamente um destes estados:

`Proposed` · `Approved` · `Planned` · `In Progress` · `Implemented` ·
`Deprecated` · `Rejected`

### Ciclo obrigatório

```text
Trigger
  ↓
ADR
  ↓
Astera Flow
  ↓
Implementação
  ↓
Validação e atualização deste documento
```

O gatilho apenas torna a evolução elegível para análise. A implementação só
começa após ADR registrada e decisão correspondente no Astera Flow. Nenhuma
ideia proposta pode ser tratada como requisito de implementação.

### Escala de impacto

Cada registro deve informar:

| Campo | Escala |
|---|---|
| **Impact** | Kernel / Provider / Operational / Enterprise |
| **Kernel impact** | ★☆☆☆☆ a ★★★★★ |
| **Complexity** | ★☆☆☆☆ a ★★★★★ |
| **Risk** | ★☆☆☆☆ a ★★★★★ |
| **Priority** | Low / Medium / High / Critical |
| **Estimated Refactoring Cost** | Low now / Medium now / High now / High in 2 years |

### Categorias de Architecture Evolution

| Categoria | Conteúdo |
|---|---|
| **Approved Evolutions** | Evoluções aprovadas pelo backlog e aguardando gatilho/ADR/Flow |
| **Proposed Evolutions** | Ideias em análise, sem autorização de implementação |
| **Experimental Ideas** | Hipóteses isoladas, sem impacto permitido na arquitetura estável |
| **Deprecated Decisions** | Decisões substituídas, preservadas para rastreabilidade |

---

## Contexto

A implementação atual da Fase C estabeleceu:

```
TaskOrchestrator
    → CapabilityRegistry.select_best()   ← scoring hardcoded
    → ProviderRegistry
    → PluginResolver
    → plugin.invoke()
```

Este documento registra as evoluções previstas, **em ordem de prioridade**,
para implementação nas fases D, E e além.

## Approved Evolutions — classificação atual

| # | Evolução | Nível | Status | Impact | Kernel impact | Complexity | Risk | Priority | Estimated Refactoring Cost | Trigger |
|---:|---|---|---|---|---|---|---|---|---|---|
| 1 | Policy Engine | LEVEL 1 — Core | Approved | Kernel | ★★★★★ | ★★★★☆ | ★★★☆☆ | High | Low now / High in 2 years | ≥ 2 providers reais por capability |
| 2 | Provider Health | LEVEL 2 — Provider | Approved | Provider | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | High | Medium now / High in 2 years | Providers em produção e rebalanceio |
| 3 | Quality Profile | LEVEL 2 — Provider | Approved | Provider | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | Medium | Medium now / High in 2 years | Comparação clínica entre providers |
| 4 | Cost Model | LEVEL 2 — Provider | Approved | Provider | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ | Medium | Low now / Medium in 2 years | Providers pagos vs. locais |
| 5 | Capability Resolver | LEVEL 1 — Core | Approved | Kernel | ★★★★★ | ★★★★☆ | ★★★★☆ | High | Medium now / High in 2 years | Junto com Policy Engine |
| 6 | Execution Plan | LEVEL 1 — Core | Approved | Kernel | ★★★★★ | ★★★★★ | ★★★★☆ | Critical | High now / High in 2 years | Primeiro workflow multi-step do ADK |

**ADR relacionada:** `ADR-002` define a governança; uma ADR específica continua
obrigatória para todas as seis evoluções antes da
implementação. O status `Approved` representa aprovação do backlog; não
representa implementação nem dispensa a decisão correspondente no Astera Flow.

## Proposed Evolutions — catálogo inicial

| Evolução | Nível | Status | Impact | Priority | Trigger inicial |
|---|---|---|---|---|---|
| Auto Scaling | LEVEL 3 — Operational | Proposed | Operational | High | SLOs e carga sustentada acima da capacidade |
| Load Balancer | LEVEL 3 — Operational | Proposed | Operational | High | Mais de uma réplica com tráfego real |
| Circuit Breaker | LEVEL 3 — Operational | Proposed | Operational | High | Falhas repetidas em provider externo |
| Retry | LEVEL 3 — Operational | Proposed | Operational | Medium | Erros transitórios observados em produção |
| Rate Limit | LEVEL 3 — Operational | Proposed | Operational | High | Exposição pública e risco de abuso |
| Billing | LEVEL 4 — Enterprise | Proposed | Enterprise | Medium | Modelo comercial aprovado |
| Marketplace | LEVEL 4 — Enterprise | Proposed | Enterprise | Medium | Mais de um provider externo comercial |
| Multi Tenant Avançado | LEVEL 4 — Enterprise | Proposed | Enterprise | Isolamento empresarial avançado requerido |
| Licensing | LEVEL 4 — Enterprise | Proposed | Enterprise | Distribuição/licenciamento do Runtime |

As evoluções `Proposed` não alteram o Kernel e não entram na contagem de
`Approved Evolutions` até que o ciclo Trigger → ADR → Astera Flow seja
concluído.

---

## Evolução 1 — Policy Engine (substitui scoring hardcoded)

### Problema atual

O `CapabilityScorer` usa constantes numéricas hardcoded:

```python
_LANGUAGE_MATCH     = 30.0
_STREAMING_MATCH    = 20.0
_LATENCY_PENALTY    = -30.0
```

À medida que mais providers chegam (Parakeet, Whisper, Azure, Deepgram,
Google STT), o scoring vai crescer em complexidade e as regras vão se
contradizer. Manter números soltos em um arquivo vira dívida técnica.

### Solução prevista

Introduzir um **Policy Engine** entre o `TaskOrchestrator` e o `CapabilityRegistry`.

```
Task
  ↓
SelectionPolicy          ← novo
  ↓
CapabilityRegistry
  ↓
ProviderRegistry
  ↓
PluginResolver
```

#### Policies pré-definidas

| Policy | Quando usar | Critérios priorizados |
|---|---|---|
| `RealtimePolicy` | Transcrição ao vivo, consulta em andamento | Streaming, latência < 150ms |
| `BatchPolicy` | Processamento offline, SOAP pós-consulta | Acurácia, custo |
| `LowLatencyPolicy` | APIs síncronas, tempo-real | Latência < 100ms, GPU |
| `HighAccuracyPolicy` | Laudos, documentos clínicos | Acurácia > 0.95, confiança |
| `OfflinePolicy` | Sem internet, dados sensíveis | Somente providers locais |
| `LowCostPolicy` | Ambientes de desenvolvimento, testes | Custo $0, sem GPU |

#### Interface prevista

```python
# Em vez de:
registry.select_best(CapabilityType.SPEECH_TRANSCRIPTION, criteria)

# O ADK faz:
orchestrator.execute(
    TaskIntent(
        capability_type=CapabilityType.SPEECH_TRANSCRIPTION,
        payload=audio_bytes,
        context=context_scope,
        policy=RealtimePolicy(),       # ← novo
    )
)
```

#### Estrutura de arquivos esperada

```
application/
  policies/
    base.py             # SelectionPolicy (Protocol)
    realtime.py         # RealtimePolicy
    batch.py            # BatchPolicy
    low_latency.py      # LowLatencyPolicy
    high_accuracy.py    # HighAccuracyPolicy
    offline.py          # OfflinePolicy
    low_cost.py         # LowCostPolicy
```

**Gatilho para implementar:** quando houver ≥ 2 providers reais registrados
para a mesma CapabilityType.

---

## Evolução 2 — ProviderHealth (saúde dinâmica por provider)

### Problema atual

`HealthStatus` é estático: `HEALTHY | DEGRADED | UNHEALTHY | UNKNOWN`.
Não reflete métricas em tempo real.

### Solução prevista

Criar a entidade `ProviderHealth`, atualizada periodicamente pelo Kernel
e usada pelo scorer/policy para ajuste dinâmico do score.

```python
@dataclass
class ProviderHealth:
    provider: ProviderName
    status: HealthStatus
    avg_latency_ms: float        # média dos últimos 60s
    p99_latency_ms: float        # percentil 99
    error_rate: float            # 0.0 – 1.0 (últimos 5 min)
    queue_size: int              # jobs pendentes
    gpu_utilization: float | None  # 0.0 – 1.0
    last_checked: datetime
```

O scorer passaria a usar `ProviderHealth` ao invés dos metadados
estáticos do `CapabilityDescriptor`:

```python
# Hoje: score baseado em avg_latency_ms estático do descriptor
# Amanhã: score baseado em ProviderHealth.avg_latency_ms em tempo real
```

**Fonte dos dados:** Prometheus / OpenTelemetry → ProviderHealth (via health check loop no Kernel).

**Gatilho para implementar:** quando houver providers rodando em produção
e o Kernel precisar re-balancear carga automaticamente.

---

## Evolução 3 — QualityProfile (substitui `accuracy_score`)

### Problema atual

`CapabilityDescriptor.accuracy_score` é um único float (0.0–1.0),
insuficiente para comparar providers em contextos clínicos.

### Solução prevista

```python
@dataclass(frozen=True)
class QualityProfile:
    accuracy_score: float        # 0.0 – 1.0
    robustness_score: float      # tolerância a ruído/variação
    stability_score: float       # consistência entre invocações
    language_coverage: int       # número de idiomas suportados
    streaming_quality: float     # qualidade em modo streaming vs. batch
    medical_terminology: bool    # suporte a vocabulário clínico
    confidence_calibration: bool # confiança alinhada com accuracy real
```

O `CapabilityDescriptor` passaria a usar `QualityProfile` no lugar de
`accuracy_score` isolado.

**Gatilho para implementar:** quando o sistema precisar comparar providers
de forma clínica (ex: Parakeet vs. Azure Speech para transcrição médica).

---

## Evolução 4 — `estimated_cost` no CapabilityDescriptor

### Problema atual

Nenhum provider declara custo. Não há como o Kernel escolher
entre uma opção gratuita (Parakeet local) e uma paga (OpenAI Whisper API).

### Solução prevista

```python
@dataclass
class CapabilityDescriptor:
    ...
    estimated_cost_per_call: Decimal | None = None   # USD
    estimated_cost_per_minute: Decimal | None = None # USD, para speech
    cost_model: Literal["per_call", "per_minute", "free", "unknown"] = "unknown"
```

O `LowCostPolicy` filtraria providers com `cost_model == "free"` primeiro.

**Gatilho para implementar:** quando o sistema tiver providers pagos
(OpenAI, Azure, Deepgram, Google) competindo com providers locais.

---

## Evolução 5 — CapabilityResolver (separar registro de resolução)

### Problema atual

O `CapabilityRegistry` faz duas coisas:
1. Indexa descriptors (registro)
2. Seleciona o melhor provider (resolução)

### Solução prevista

```
CapabilityRegistry   → indexação pura (register, unregister, list)
     ↓
CapabilityResolver   → resolução (select_best, query, policy application)
     ↓
ProviderRegistry
     ↓
PluginResolver
```

```python
class CapabilityResolver:
    def __init__(
        self,
        registry: CapabilityRegistry,
        provider_registry: ProviderRegistry,
        health_monitor: ProviderHealthMonitor,  # Evolução 2
    ) -> None: ...

    def resolve(
        self,
        capability_type: CapabilityType,
        policy: SelectionPolicy,                # Evolução 1
    ) -> ResolvedCapability: ...
```

**Gatilho para implementar:** junto com a Evolução 1 (Policy Engine),
pois ambas fazem sentido juntas.

---

## Evolução 6 — ExecutionPlan (Orchestrator não executa, planeja)

### A mudança mais impactante

Esta é a evolução que vai habilitar o Google ADK e workflows clínicos complexos.

### Problema atual

O `TaskOrchestrator` executa uma capability por vez:

```
TaskIntent → select_best → invoke → TaskResult
```

Isso não suporta workflows como:

```
SOAP Note
  Step 1: SPEECH_TRANSCRIPTION  (áudio → texto)
  Step 2: NLP_ENTITY_EXTRACTION (texto → entidades clínicas)
  Step 3: MEDICAL_SOAP_GENERATION (entidades → SOAP)
  Step 4: MEDICAL_ICD_CODING (diagnósticos → CID-10)
```

### Solução prevista

O `TaskOrchestrator` passa a montar um **ExecutionPlan** antes de executar.
O plano define as etapas, dependências e paralelismo.

```python
@dataclass
class ExecutionStep:
    capability_type: CapabilityType
    policy: SelectionPolicy
    depends_on: list[str] = field(default_factory=list)  # step IDs
    input_mapping: dict[str, str] = field(default_factory=dict)

@dataclass
class ExecutionPlan:
    plan_id: str
    steps: list[ExecutionStep]
    context: ContextScope
    created_at: datetime
```

#### Fluxo com ExecutionPlan

```
TaskIntent (multi-step)
  ↓
ExecutionPlanner.plan()    ← novo
  ↓
ExecutionPlan
  ↓
PlanExecutor.run()         ← novo (substitui invoke direto)
  ├── Step 1: CapabilityResolver → PluginResolver → invoke
  ├── Step 2: CapabilityResolver → PluginResolver → invoke
  └── Step 3: CapabilityResolver → PluginResolver → invoke
  ↓
TaskResult (agregado)
```

#### Estrutura de arquivos esperada

```
application/
  orchestrator/
    task_intent.py        ← já existe
    task_result.py        ← já existe
    orchestrator.py       ← já existe (refatorar para usar planner)
    execution_plan.py     ← novo
    execution_step.py     ← novo
    execution_planner.py  ← novo
    plan_executor.py      ← novo
```

**Gatilho para implementar:** quando o Google ADK precisar orquestrar
mais de uma capability em sequência (Fase D/E — primeiro workflow clínico).

---

## Resumo — classificação, gatilho e governança

| # | Evolução | Nível | Status | Gatilho | Fase estimada | ADR |
|---|---|---|---|---|---|---|
| 1 | Policy Engine | Core | Approved | ≥ 2 providers reais por capability | D/E | Obrigatória |
| 2 | ProviderHealth dinâmica | Provider | Approved | Providers em produção, rebalanceio de carga | E | Obrigatória |
| 3 | QualityProfile | Provider | Approved | Comparação clínica entre providers | E | Obrigatória |
| 4 | Cost Model | Provider | Approved | Providers pagos vs. locais | E | Obrigatória |
| 5 | CapabilityResolver | Core | Approved | Junto com Policy Engine | D/E | Obrigatória |
| 6 | ExecutionPlan | Core | Approved | Primeiro workflow multi-step do ADK | D | Obrigatória |

---

## Regra de ouro

> Não implemente uma evolução antes do gatilho, da ADR e da decisão do Astera
> Flow. Cada uma adiciona complexidade real. Registrar é suficiente até que o
> contexto justifique a mudança.

---

*Documento criado: 2026-08-07*
*Última atualização: 2026-08-07 12:43:57 -03:00*
*Revisão: Architecture Evolution governance*
# Histórico — Architecture Evolution Backlog

> **Status:** Encerrado para novas implementações pela [ADR-011 — Platform Complete](../adrs/ADR-011-platform-complete.md).
> Os itens abaixo permanecem como registro histórico. O trabalho ativo está no
> [Product Backlog](product-backlog.md).
