# README do Astera Flow

> Ponto oficial de entrada para qualquer agente de IA ou desenvolvedor.

## O que é o Astera?

Astera é a plataforma de referência para documentação, arquitetura, engenharia e execução operacional do ecossistema Astera Flow.

## Como esta documentação está organizada?

A documentação está dividida em áreas principais:

- Product: visão, contexto e objetivos de produto.
- Architecture: arquitetura e decisões estruturais.
- Engineering: planos, execução e implementação.
- Knowledge: fontes e conhecimento médico.
- ADRs: registros de decisões arquiteturais.
- Astera Flow: especificação operacional e fluxo de execução.

## Por onde eu começo?

Comece sempre pela sequência oficial:

1. AGENTS.md
2. ASTERA_INDEX.md
3. DOCUMENT_CONVENTIONS.md
4. GLOSSARY.md
5. Astera Flow

## Quais documentos são obrigatórios?

Todos os agentes devem ler obrigatoriamente:

- AGENTS.md
- ASTERA_INDEX.md
- DOCUMENT_CONVENTIONS.md
- GLOSSARY.md
- Astera Flow
- Constituição de Engenharia (`engineering/README.md` e documentos
  `engineering/ASTERA-ENG-*.md` aplicáveis)

## Hierarquia de governança

Em conflitos, a ordem oficial é:

1. Constituição de Engenharia;
2. ADRs;
3. AGENTS.md;
4. documentação complementar;
5. README.

Essa ordem é instituída pelo [ADR-015 — Engineering Governance](adrs/ADR-015-engineering-governance.md).
Os documentos são obrigatórios para desenvolvimento humano, agentes de IA,
revisão de código, validação de PR, Definition of Done, auditorias e releases.
