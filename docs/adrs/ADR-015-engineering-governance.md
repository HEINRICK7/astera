---
document_id: astera-adr-015
title: Engineering Governance
category: Architecture Governance
status: Accepted
version: 1.0
owner: Astera Architecture
depends_on:
  - ../AGENTS.md
  - ../ASTERA_INDEX.md
  - ../engineering/README.md
used_by:
  - Human Engineers
  - AI Agents
  - Code Review
  - PR Validation
  - Runtime Audit
  - Release Engineering
last_updated: 2026-08-10
---

# ADR-015 — Engineering Governance

| Campo | Valor |
|---|---|
| **Status** | Accepted |
| **Data** | 2026-08-10 |
| **Decisor** | Astera Architecture |
| **Categoria** | Architecture Governance |
| **Escopo** | Desenvolvimento, Runtime, integração, auditoria, validação e release |

## Objetivo

Instituir a Constituição de Engenharia do Astera como camada normativa para
provar que decisões arquiteturais são implementadas, integradas e executadas.

## Contexto

O `AGENTS.md` determinava que não fossem criados novos documentos de engenharia
fora do Astera Flow. Essa regra protegia o projeto contra documentação paralela,
mas tornou-se insuficiente quando o Astera passou a exigir evidências de
execução, auditoria de Runtime, governança de providers, traces e gates de
release.

Código compilando, teste unitário passando e documentação técnica dizendo
“implementado” não provam que uma consulta real percorreu o Runtime até a tela.

## Decisão

Criar `docs/engineering/` como a Constituição de Engenharia oficial do Astera.
Os documentos `ASTERA-ENG-001` a `ASTERA-ENG-011` definem regras de processo e
evidência. Eles não criam novos domínios clínicos nem substituem ADRs de
arquitetura; tornam verificável a execução das decisões existentes.

A hierarquia normativa passa a ser:

```text
1. Constituição de Engenharia (ASTERA-ENG)
2. ADRs
3. AGENTS.md
4. Documentação complementar
```

Em caso de conflito, uma regra antiga que impeça auditoria, integração ou
validação correta do Runtime deve ser atualizada explicitamente, com a
justificativa registrada na mudança correspondente.

## Arquitetura de governança

```text
ADR → Arquitetura → Implementação → Integração → Audit → Trace
  → Consulta Real → Validação Visual → Release
```

O `AGENTS.md` continua definindo o comportamento geral dos agentes. O Astera
Flow continua sendo a especificação operacional e o registro de execução. A
Constituição de Engenharia prevalece quando a regra operacional anterior não
fornecer prova suficiente de uso no Runtime.

## Responsabilidades

Os documentos ASTERA-ENG são obrigatórios para:

- desenvolvimento humano;
- agentes de IA;
- revisão de código;
- validação de PR;
- definição de Done;
- auditorias;
- releases.

O índice em [docs/engineering/README.md](../engineering/README.md) é a entrada
única da Constituição. Não devem ser criados documentos redundantes para as
mesmas regras.

## Fluxo

Toda funcionalidade deve seguir o workflow definido no
[ASTERA-ENG-011](../engineering/ASTERA-ENG-011-engineering-workflow.md) e só
pode ser liberada após o gate definido no
[ASTERA-ENG-010](../engineering/ASTERA-ENG-010-release-gate.md).

## Princípios

- Implementado não significa integrado.
- Integrado não significa validado.
- Código e testes não substituem consulta real.
- O Runtime é a fonte operacional da verdade.
- React projeta o estado observado e não cria a verdade clínica.
- Toda Sprint termina com auditoria e evidência.

## Consequências

- A regra antiga contra documentação paralela permanece válida para documentos
  redundantes de arquitetura, planejamento e roadmap.
- `docs/engineering/` é uma exceção formal, versionada e referenciada pelo
  índice principal.
- Toda nova regra de governança deve atualizar este ADR ou criar um novo ADR,
  preservando o histórico.
- Uma feature sem validação em consulta real permanece incompleta.

## Critérios

Esta decisão é considerada aplicada quando:

- o ADR aparece no índice de ADRs;
- a Constituição aparece no índice principal;
- o `AGENTS.md` referencia a hierarquia;
- os documentos ASTERA-ENG referenciam este ADR;
- revisões e releases usam os gates definidos.

## Referências

- [ASTERA-ENG README](../engineering/README.md)
- [ASTERA-ENG-001 — Runtime Definition of Done](../engineering/ASTERA-ENG-001-runtime-definition-of-done.md)
- [ASTERA-ENG-011 — Engineering Workflow](../engineering/ASTERA-ENG-011-engineering-workflow.md)
- [AGENTS.md](../AGENTS.md)
- [ASTERA_INDEX.md](../ASTERA_INDEX.md)
