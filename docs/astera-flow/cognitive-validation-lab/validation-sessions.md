# Validation Sessions

| Campo | Valor |
|---|---|
| **Status** | Proposed |
| **Responsável** | Cognitive Validator |
| **Entrada** | Um caso do Case Registry |
| **Saída** | Validation Report versionado |

## Objetivo

Executar uma sessão de validação do modelo cognitivo sem usar IA, ADK ou código
de produção para interpretar o caso.

## Etapas

1. Leitura clínica cega do caso.
2. Extração de Clinical Facts.
3. Construção de versões do Clinical Context.
4. Registro de Hypotheses e Information Gaps.
5. Registro de Knowledge Queries e referências necessárias.
6. Derivação de SOAP/Clinical Representation.
7. Comparação com a consulta original.
8. Registro de perdas, criações, confusões e conceitos ausentes.

## Validation Report

```text
ValidationReport
├── report_id / case_id / session_version
├── source_provenance
├── clinical_facts_score
├── clinical_context_score
├── hypotheses_score
├── knowledge_queries_score
├── representation_score
├── information_loss
├── invented_information
├── concept_confusion
├── missing_concepts
├── architecture_changes_needed
├── implementation_changes_needed
├── evidence
└── verdict: pass | pass_with_gaps | fail
```

## Exemplo de nota

```text
Case: Cardiology 001
Clinical Facts: 98%
Clinical Context: 100%
Hypotheses: 92%
Knowledge Queries: 100%
SOAP: 95%
Information Loss: 2%
Invented Information: 0%
Architecture Changes Needed: No
Verdict: pass_with_gaps
```

As métricas não são probabilidade clínica nem medem qualidade de LLM. Elas
medem fidelidade de representação contra o caso e a anotação de referência.
