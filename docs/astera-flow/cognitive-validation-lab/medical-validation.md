# Medical Validation

| Campo | Valor |
|---|---|
| **Status** | Not Started |
| **Pré-requisito** | Reality Review / Cognitive Validation Lab |
| **Responsável** | Medical Validator |

## Objetivo

Validar se o modelo cognitivo representa corretamente o raciocínio clínico,
depois que os casos passaram pelo Cognitive Validation Lab.

## Fronteira

```text
Cognitive Validation Lab
  pergunta: “Conseguimos representar a consulta?”
          ↓
Medical Validation
  pergunta: “A representação está clinicamente correta?”
```

Medical Validation não substitui a Reality Review e não valida um fornecedor de
IA isoladamente.

## Entrada mínima

- Validation Reports dos dez casos;
- Failure Analysis concluída;
- casos e fontes com acesso autorizado;
- decisões arquiteturais abertas explicitadas;
- annotator/validator provenance.

## Saída

```text
MedicalValidationReport
├── case_reports
├── clinical_accuracy_findings
├── unsafe_or_incomplete_reasoning
├── reviewer_decisions
├── required_architecture_changes
└── verdict: approved | approved_with_conditions | rejected
```

Nenhuma implementação da Fase D deve ser promovida por este documento antes
do verdict formal no Astera Flow.
