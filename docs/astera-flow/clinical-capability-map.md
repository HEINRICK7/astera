---
document_id: astera-clinical-capability-map
title: Clinical Capability Map
category: Product Domain
status: Official
priority: P0
owner: Astera Clinical Product
depends_on:
  - clinical-capability-catalog.md
  - product-backlog.md
last_updated: 2026-08-08
---

# Clinical Capability Map

O mapa mostra quem usa cada capacidade e como o Astera evolui de uma entrada
simples até uma consulta clínica completa. Ele é uma visão de domínio, não um
diagrama de componentes.

## Mapa por participante

```text
Paciente
├── CC-001  Entrar na consulta
├── CC-002  Consentir
└── CC-003  Conectar áudio e vídeo

Médico
├── CC-004  Criar e iniciar consulta
├── CC-005  Conduzir sessão ativa
└── CC-010  Revisar e aprovar SOAP

Comunicação
├── CC-003  Áudio e vídeo
└── CC-005  Sessão e encerramento

Inteligência clínica
├── CC-006  Speech
├── CC-007  Clinical Facts
├── CC-008  Context e Reasoning
└── CC-009  Knowledge e Clinical Events

Revisão e continuidade
├── CC-010  SOAP
├── CC-011  FHIR
└── CC-012  Salvar e auditar
```

## Mapa da Consulta Primária

```text
CC-001 Paciente entra
        ↓
CC-002 Paciente consente
        ↓
CC-003 Áudio e vídeo conectam
        ↓
CC-004 Médico inicia
        ↓
CC-005 Consulta acontece
        ↓
CC-006 Conversa é transcrita
        ↓
CC-007 Fatos clínicos são identificados
        ↓
CC-008 Contexto e raciocínio são organizados
        ↓
CC-009 Conhecimento aparece
        ↓
CC-010 Médico revisa e aprova SOAP
        ↓
CC-011 Resultado é representado em FHIR
        ↓
CC-012 Consulta é salva e auditada
```

## Relação com Workflows

| Workflow | Capabilities principais |
|---|---|
| Consulta Primária | CC-001 a CC-012 |
| Consulta com Exame | CC-001 a CC-005, CC-007 a CC-012 |
| Consulta Pediátrica | CC-001 a CC-005, CC-006 a CC-012 |
| Consulta de Retorno | CC-001 a CC-005, CC-007 a CC-012 |
| Consulta de Emergência | CC-001 a CC-005, CC-007 a CC-012, com revisão reforçada |

Uma Capability pode aparecer em vários Workflows. O Workflow define o caso de
uso clínico; a Capability define o comportamento reutilizável.

## Relação com Clinical Scenarios

| Scenario | Resultado esperado |
|---|---|
| Dor de cabeça | O médico conduz a consulta e recebe documentação revisável |
| Hipertensão | Condição e medicamento aparecem relacionados e rastreáveis |
| Pediatria | Paciente, responsável e relato permanecem corretamente atribuídos |
| Retorno | O médico compara a consulta atual com o contexto autorizado |

O mesmo mapa de capacidades sustenta cenários diferentes. O cenário muda o
conteúdo clínico; não cria uma arquitetura paralela.

## Regra do mapa

Se uma entrega não puder ser localizada neste mapa como uma nova capacidade
clínica observável, ela é trabalho habilitador e não pode ser apresentada como
resultado principal da Sprint.
