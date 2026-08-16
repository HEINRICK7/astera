---
document_id: astera-executive-dashboard
title: Astera Executive Dashboard
category: Product
status: Official
version: 2.0
owner: Astera Product Engineering
depends_on:
  - product-backlog.md
  - clinical-workflows/README.md
  - clinical-workflows/clinical-workflow-dataset.md
used_by:
  - Product
  - Clinical Validation
  - Demo Day
last_updated: 2026-08-07
---

# Astera Executive Dashboard

Atualizado em **2026-08-07**.

## Platform

🟢 Stable · Architecture v1.0 · Platform Complete · ADR-011

## Operating Model

O Astera opera em **Product Engineering**. A arquitetura base está encerrada;
o trabalho ativo é concluir Clinical Product Increments (CPIs) que entreguem
valor revisável ao médico. Capabilities, Providers e evidências são meios de
execução.

Backlog oficial: [Product Backlog](product-backlog.md).
Roteiro de validação com médicos: [Demo Day](demo-day.md).

## Foundation Models — Google ADK

| Boundary | Status |
|---|---|
| Google ADK | 🟢 Active |
| Foundation Model adapter | 🟢 Implemented |
| Model-specific coupling in Kernel | 🟢 None |
| Production model | ⚪ Configurable by organization |

## Capabilities

| Capability | Engineering | Validation | Certification | Production |
|---|---|---|---|---|
| Speech | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |
| Vision | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |
| OCR | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |
| Medical NLP | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |
| Terminology | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |
| FHIR | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |
| Embeddings | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |
| Knowledge | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |
| Reasoning | 🟡 Complete / deterministic | ⚪ Pending | ⚪ Not issued | ⚪ Not ready |

## Providers

| Capability | Development Provider | Benchmark Provider | Production |
|---|---|---|---|
| Speech | faster-whisper ✅ | NVIDIA Parakeet NIM 🟡 | ⚪ Not certified |
| Vision | Pending policy registration | Qwen-VL candidate | ⚪ Not certified |
| Terminology | Snowstorm ✅ | Pending | ⚪ Not certified |
| Embeddings | multilingual-e5-small ✅ | BGE-M3 | ⚪ Not certified |
| FHIR | HAPI FHIR ✅ | Pending | ⚪ Not certified |

## Indicador oficial

O indicador primário é o estado do Clinical Product Increment e a quantidade de
workflows clínicos concluídos com evidência. Commits, número bruto de testes e
status de componentes são sinais de engenharia, não indicadores de produção.

## Primary Care Workflow — CPI-001

**Sprint question:** O Astera consegue concluir uma consulta clínica simples do
início ao fim?  
**Sprint result:** Blocked — falta executar áudio autorizado com persistência
real e replay completo.

| Etapa clínica | Estado | Leitura para produto |
|---|---|---|
| Transcript | ✅ | Contrato e harness validados; áudio clínico real ainda pendente |
| Clinical Facts | ✅ | Extração e provenance validadas no harness |
| Clinical Context | ✅ | Contexto e timeline disponíveis no replay |
| Reasoning | 🟡 | Pipeline integrado; validação em consulta real pendente |
| Knowledge | 🟡 | Queries e referências integradas; evidência clínica pendente |
| SOAP | 🟢 | Representação gerada e revisável no fluxo determinístico |
| FHIR | ⚪ | Gateway real e persistência ainda pendentes |
| Production | ⚪ | Não promover antes dos gates clínicos e operacionais |

**CPI-001:** 🟡 Em execução — resultado ainda não emitido  
**Golden Consultation 001:** 🟡 Roteiro pronto; gravação autorizada pendente  
**Real Consultation Success Rate:** N/A — nenhuma consulta real certificada  
**SOAP Acceptance Rate:** N/A — revisão médica ainda não coletada

## Métricas do produto

| Métrica | Estado atual | Fonte |
|---|---|---|
| Workflows iniciados | 0 com áudio real | Clinical Workflow Dataset |
| Workflows concluídos | 0 certificados | Clinical Replay |
| Critical Fact Recall | N/A | Avaliação clínica por caso |
| Unsupported Content Rate | N/A | CQA e revisão médica |
| SOAP Acceptance Rate | N/A | Revisão do médico |
| FHIR Validity Rate | N/A | Gateway e replay |
| Persistência recuperável | ⚪ Pendente | Clinical Replay |

O dashboard nunca transforma ausência de medição em zero e nunca transforma
execução determinística em produção.

## Provider Evidence

| Indicador | Speech |
|---|---|
| Capability Independence Score | Ainda não medido — Parakeet não integrado |
| Provider Replaceability Index | Ainda não medido |
| Clinical Workflow Dataset | v1.1 em preparação |
| Provider Trace | Implementado no evidence path |
| Clinical Domain conhece ProviderTrace | Não |

Detalhes e critérios: [Provider Evidence Metrics](benchmarks/provider-evidence-metrics.md).

## Clinical Journey

### Clinical Product Increments

| Incremento | Caso de uso | Estado |
|---|---|---|
| CPI-001 | Primary Care Consultation | 🟡 Em execução |
| CPI-002 | Consulta com Exame | ⚪ Ready |
| CPI-003 | Consulta Pediátrica | ⚪ Planned |
| CPI-004 | Consulta de Retorno | ⚪ Planned |

| Etapa | Estado |
|---|---|
| Speech | 🟢 Development Provider approved · Benchmark Provider pendente |
| Clinical Facts | 🟢 Harness validado |
| Clinical Context | 🟢 Harness validado |
| Reasoning | 🟢 Harness validado |
| Knowledge | 🟢 Harness validado |
| SOAP | 🟢 Harness validado |
| FHIR | 🟡 Gateway real pendente |
| Persistence | 🟡 Persistência durável pendente |

**Real Consultation Success Rate:** não medido.  
**Clinical Workflow Certification:** não emitida.  

O detalhe da Capability Zero está em
[Clinical Workflow Certification](clinical-workflows/README.md) e no
[Clinical Workflow Dataset](clinical-workflows/clinical-workflow-dataset.md).

## Apêndice de engenharia

O estado de Capabilities e Providers continua disponível para a equipe técnica,
mas fica subordinado ao progresso do workflow. Ele responde “como o Astera
entrega?”; o quadro acima responde “qual consulta o médico consegue concluir?”.
