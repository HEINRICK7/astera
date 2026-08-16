# Cognitive Validation Lab

Área permanente do Astera Flow para validar capabilities, modelo cognitivo e
raciocínio clínico da plataforma.

```text
Astera Flow
└── Cognitive Validation Lab
    ├── Case Registry
    ├── Validation Sessions
    ├── Failure Analysis
    ├── Edge Cases
    ├── Regression Suite
    ├── Benchmark Results
    └── Medical Validation
```

## Propósito

O Lab não valida apenas um LLM, Speech provider, RAG ou implementação. Ele
pergunta se uma capability continua representando corretamente consultas
clínicas quando providers, plugins e tecnologias mudam.

O Cognitive Validation Lab é o processo de **Cognitive QA (CQA)** do Astera.

## Dois pipelines independentes

```text
Pipeline de Desenvolvimento
Astera Flow → Arquitetura → Código → Testes de Software

Pipeline de Validação Cognitiva de Capability
Capability → Caso Clínico → Clinical Facts → Clinical Context → Reasoning
           → Knowledge → SOAP → Comparação → Validation Report
           → Regression → Certification Evidence
```

Os pipelines podem trocar artefatos versionados e resultados, mas não misturam
seus critérios de sucesso. `pytest` responde se o software funciona; CQA
responde se o modelo cognitivo representa o atendimento.

## Agentes pesquisadores

- **Case Curator:** encontra, verifica acesso/licença, desidentifica quando
  permitido, classifica e registra casos.
- **Cognitive Validator:** compara a consulta com Facts, Context, Hypotheses,
  Knowledge e Representations.
- **Gap Detector:** identifica conceito, entidade, relação ou estado ausente.
- **Architecture Reviewer:** decide se o achado exige mudança arquitetural ou
  apenas correção de implementação.

Esses agentes produzem relatórios e evidências. Eles não implementam código.

## Documentos do Lab

- [Case Registry](case-registry.md)
- [Validation Sessions](validation-sessions.md)
- [Failure Analysis](failure-analysis.md)
- [Edge Cases](edge-cases.md)
- [Regression Suite](regression-suite.md)
- [Benchmark Results](benchmark-results.md)
- [Medical Validation](medical-validation.md)

## Regra de promoção

```text
Caso Clínico
   ↓
Validation Report
   ↓
Failure Analysis / Gap Detection
   ↓
Architecture Decision
   ↓
Astera Flow
   ↓
Implementação, se autorizada
```

Um caso não gera código diretamente. Ele gera evidência sobre o modelo.
