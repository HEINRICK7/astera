---
document_id: astera-clinical-capability-catalog
title: Clinical Capability Catalog
category: Product Domain
status: Official
priority: P0
owner: Astera Clinical Product
depends_on:
  - product-backlog.md
  - vision-demo.md
  - definition-of-done.md
used_by:
  - Product
  - Product Engineering
  - Clinical Validation
  - Runtime Capability Catalog
last_updated: 2026-08-08
---

# Clinical Capability Catalog

O Clinical Capability Catalog é a fonte oficial das capacidades clínicas que o
Astera entrega. Ele mede comportamento observável no produto, não Features,
Stories, Tasks, classes ou providers.

```text
Clinical Capability
  ├── Descrição
  ├── Dependências
  ├── Journeys
  ├── Clinical Workflows
  ├── Clinical Scenarios
  ├── Critérios de aceite
  ├── Evidência de demonstração
  └── Status de maturidade
```

Uma Capability pode participar de vários Workflows e vários Clinical Scenarios.
O provider ou componente utilizado para entregá-la é detalhe de implementação
e não altera sua identidade.

## Catálogo oficial

| ID | Capability | Journey principal | Status |
|---|---|---|---:|
| CC-001 | Paciente consegue entrar na consulta | Patient Journey | 🟡 |
| CC-002 | Paciente concede consentimento | Patient Journey | ⚪ |
| CC-003 | Paciente e médico conectam áudio e vídeo | Communication Journey | ⚪ |
| CC-004 | Médico inicia a consulta | Doctor / Consultation Journey | ⚪ |
| CC-005 | Consulta acontece com sessão ativa | Consultation Journey | ⚪ |
| CC-006 | Conversa é transcrita | Clinical Journey | ⚪ |
| CC-007 | Fatos clínicos são identificados | Clinical Journey | ⚪ |
| CC-008 | Contexto e raciocínio clínico são organizados | Clinical Journey | ⚪ |
| CC-009 | Conhecimento aparece durante a consulta | A2UI Journey | ⚪ |
| CC-010 | Médico revisa e aprova o SOAP | Clinical Review Journey | ⚪ |
| CC-011 | Resultado clínico é representado em FHIR | Clinical Review Journey | ⚪ |
| CC-012 | Consulta é salva e pode ser auditada | Operations Journey | ⚪ |

## Definições das capacidades

### CC-001 — Paciente consegue entrar na consulta

- **Descrição:** o paciente abre o convite no celular e chega à sala de espera.
- **Dependências:** convite válido e consulta agendada.
- **Journeys:** Patient Journey.
- **Workflows:** Consulta Primária.
- **Clinical Scenarios:** todos os cenários com consulta remota.
- **Critérios:** o paciente identifica a consulta, entra sem instalar aplicativo
  e vê uma confirmação clara.
- **Demo:** `patient-journey-demo.mp4`, cenas 1 a 5 da Vision Demo.
- **Status:** 🟡 Em desenvolvimento.

### CC-002 — Paciente concede consentimento

- **Descrição:** o paciente entende e registra sua decisão sobre dados,
  câmera, microfone e documentação clínica.
- **Dependências:** CC-001.
- **Journeys:** Patient Journey.
- **Workflows:** Consulta Primária.
- **Clinical Scenarios:** todos os cenários que utilizam comunicação ou
  documentação assistida.
- **Critérios:** aceite ou recusa explícitos, rastreáveis e apresentados em
  linguagem compreensível.
- **Demo:** `patient-journey-demo.mp4`, cena 3.
- **Status:** ⚪ Não iniciado.

### CC-003 — Paciente e médico conectam áudio e vídeo

- **Descrição:** duas pessoas conseguem se ver e se ouvir durante a consulta.
- **Dependências:** CC-001, CC-002, pré-check de dispositivos.
- **Journeys:** Communication Journey.
- **Workflows:** Consulta Primária.
- **Clinical Scenarios:** Dor de cabeça, Hipertensão e demais consultas remotas.
- **Boundary:** [Communication Platform Architecture](../../astera-workbench/docs/communication-platform-architecture.md).
- **Critérios:** notebook e smartphone conectados, áudio e vídeo fluidos,
  reconexão tratada e qualidade compreensível.
- **Demo:** `communication-journey-demo.mp4`.
- **Status:** ⚪ Não iniciado.

### CC-004 — Médico inicia a consulta

- **Descrição:** o médico vê que o paciente está pronto e inicia o atendimento.
- **Dependências:** CC-001, CC-002, CC-003.
- **Journeys:** Doctor Journey, Consultation Journey.
- **Workflows:** Consulta Primária.
- **Clinical Scenarios:** todos os cenários com atendimento remoto.
- **Critérios:** o médico identifica o paciente conectado, inicia com uma ação
  clara e vê o estado da sessão mudar.
- **Demo:** `doctor-journey-demo.mp4`.
- **Status:** ⚪ Não iniciado.

### CC-005 — Consulta acontece com sessão ativa

- **Descrição:** a consulta possui participantes, estado, tempo, início e
  encerramento compreensíveis.
- **Dependências:** CC-003, CC-004.
- **Journeys:** Consultation Journey.
- **Workflows:** Consulta Primária.
- **Clinical Scenarios:** Dor de cabeça, Hipertensão, Pediatria e Retorno.
- **Critérios:** espera, sessão ativa, pausa, encerramento e timeline podem ser
  observados sem explicar a arquitetura ao médico.
- **Demo:** `consultation-journey-demo.mp4`.
- **Status:** ⚪ Não iniciado.

### CC-006 a CC-012 — Capacidades clínicas posteriores

| ID | Descrição | Dependências | Journeys | Workflow / Scenario | Critério e Demo | Status |
|---|---|---|---|---|---|---:|
| CC-006 | Conversa é transcrita | CC-005 | Clinical | Consulta Primária / Dor de cabeça | Transcript completo e revisável; `clinical-journey-demo.mp4` | ⚪ |
| CC-007 | Fatos clínicos são identificados | CC-006 | Clinical | Consulta Primária / Hipertensão | Fatos rastreáveis ao que foi dito; `clinical-journey-demo.mp4` | ⚪ |
| CC-008 | Contexto e raciocínio são organizados | CC-007 | Clinical | Consulta Primária / Dor de cabeça | Hipóteses e lacunas permanecem revisáveis; `clinical-journey-demo.mp4` | ⚪ |
| CC-009 | Conhecimento aparece durante a consulta | CC-008 | A2UI | Consulta Primária / Dor de cabeça | Evento clínico vira representação visível; `a2ui-journey-demo.mp4` | ⚪ |
| CC-010 | Médico revisa e aprova o SOAP | CC-009 | Clinical Review | Consulta Primária / Dor de cabeça | Médico corrige e aprova sem editar logs; `clinical-review-journey-demo.mp4` | ⚪ |
| CC-011 | Resultado clínico é representado em FHIR | CC-010 | Clinical Review | Consulta Primária / Hipertensão | Representação validada e rastreável; `clinical-review-journey-demo.mp4` | ⚪ |
| CC-012 | Consulta é salva e pode ser auditada | CC-010, CC-011 | Operations | Todos os Workflows | Consulta recuperável com histórico; `operations-journey-demo.mp4` | ⚪ |

Cada linha segue o mesmo contrato de aceite: dependência explícita, Workflow,
Clinical Scenario, comportamento observável, vídeo e validação profissional.

## Estados de maturidade

```text
⚪ Não iniciado
🟡 Em desenvolvimento
🔵 Em validação
🟢 Demonstrado e aprovado
🔴 Bloqueado
```

Uma Capability só recebe 🟢 quando atende integralmente ao [Definition of
Done](definition-of-done.md). O status nunca é calculado pelo número de testes
ou linhas de código.

## Regra de evolução

> **Nenhuma Sprint existe para implementar uma tecnologia. Toda Sprint existe
> para entregar uma Clinical Capability que possa ser demonstrada em uma
> consulta real.**
