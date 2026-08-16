# ADR-020 — Clinical Workspace Experience

Status: Accepted  
Date: 2026-08-09

## Context

O Runtime e o Clinical Experience Engine já produzem problemas, evidências,
hipóteses, perguntas, histórico, medicação, evolução e SOAP. A apresentação,
porém, não pode ser apenas um conjunto de cards que troca o conteúdo de
artefatos técnicos.

O médico precisa acompanhar o caso como uma linha de raciocínio: situação atual,
problemas ativos, evidências, lacunas, hipóteses, próximos passos e evolução.
O workspace deve mostrar essa história sem duplicar o mesmo dado em regiões
distintas.

## Decision

O Clinical Component Catalog mantém o contrato declarativo A2UI, mas a visão
clínica é composta como um workspace cognitivo, não como um template de card:

- `ClinicalWorkspaceExperience`: situação, foco e hierarquia do caso;
- `ClinicalProblemExperience`: problema vivo que cresce com evidências e lacunas;
- `ClinicalHypothesisExperience`: possibilidade clínica com confiança e base;
- `ClinicalQuestionExperience`: próximo passo ligado ao problema;
- `ClinicalContextExperience`: apenas o contexto que muda a leitura do caso;
- história cognitiva: narrativa de como o entendimento cresceu;
- indicador compacto de progresso do SOAP, com abertura explícita da nota.

O problema em foco recebe mais espaço e peso visual. A barra lateral do
workspace mostra somente evolução/contexto; ela não replica o conteúdo central.
Runtime, JSONL, Graph e estados técnicos continuam disponíveis exclusivamente
na visão `Runtime`.

## Visual language

- ícones semânticos do catálogo Astera, sem emojis;
- tipografia e espaçamento com hierarquia editorial;
- bordas, fundos e motion específicos por tipo de objeto;
- crescimento incremental do mesmo objeto, sem substituir por outro objeto;
- estados internos traduzidos em evolução visual discreta;
- nenhuma palavra de engenharia (`fact`, `graph`, `patch`, `created`, `JSON`)
  na visão clínica.
- narrativa e progressão cognitiva no lugar de uma timeline de logs;
- divulgação progressiva: o que é secundário aparece somente quando relevante.

## Consequences

O Presentation Composer continua sendo a única fronteira de composição. Não
serão criados `CardEngine`, `WidgetEngine`, `SceneManager` ou outra camada para
resolver apresentação. Novos widgets devem entrar no catálogo somente quando
possuírem uma função clínica distinta e uma identidade visual justificável.

Runtime e Clinical View continuam sendo superfícies diferentes: a primeira pode
expor operações e diagnósticos para desenvolvimento; a segunda conta a
evolução do caso para o profissional.
