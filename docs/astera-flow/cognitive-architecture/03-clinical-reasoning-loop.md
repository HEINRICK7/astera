# 03 — Clinical Reasoning Loop

| Campo | Valor |
|---|---|
| **Status** | Approved |
| **Workshop origem** | Workshop 3 — Clinical Reasoning Model |
| **ADR** | ADR-006 |
| **Responsável** | Reasoning Specialist |

## Objetivo

Definir como Clinical Context produz hipóteses concorrentes, Information Gaps e
perguntas sem transformar o primeiro resultado em diagnóstico.

## Definições

- **Hypothesis:** explicação provisória para fatos contextualizados.
- **Information Gap:** informação ausente necessária para avaliar hipótese.
- **Reasoning cycle:** iteração do loop que pode atualizar o Context.

## Ciclo normativo

```text
Observe → Interpret → Hypothesize → Ask
    ↑                         ↓
Update Context ← Observe again
              → Refine Hypotheses ↺
```

## Entidades

```text
ClinicalHypothesis
├── id / name / confidence
├── supporting_facts / missing_facts / conflicting_facts
├── status / created_at / updated_at / provenance

InformationGap
├── id / hypothesis_id / missing_fact_type
├── importance / question / acquisition_method
└── status / provenance
```

## Exemplo

Dor torácica e dispneia podem sustentar Síndrome Coronariana Aguda e Angina
Estável simultaneamente; ECG e troponina ausentes geram Information Gaps.

## Contrato normativo

O Reasoning Specialist MUST retornar hipóteses com suporte, conflitos, lacunas,
confidence e status. `confidence` MUST NOT ser apresentada como probabilidade
clínica calibrada sem validação. Uma pergunta MUST possuir objetivo e gap ou
hipótese relacionada.

## Responsabilidades e eventos

O Specialist interpreta Context, formula hipóteses e planeja perguntas. Eventos:
`clinical.hypothesis.created`, `clinical.hypothesis.updated`,
`clinical.information_gap.detected`, `clinical.question.proposed` e
`clinical.reasoning.cycle_completed`.

## Regras e restrições

1. Hipótese não é Clinical Fact nem diagnóstico.
2. Hipóteses concorrentes devem coexistir.
3. Gap não significa que o fato é falso; significa que ainda não foi obtido.
4. A pergunta nasce da lacuna, não de texto livre sem justificativa.

## Validação

Com dor torácica, dispneia, hipertensão e histórico familiar, o sistema deve
produzir pelo menos duas hipóteses, explicitar suporte e ausência de ECG/
troponina e propor perguntas rastreáveis.

## Questões abertas

Calibração de confidence, priorização de gaps, revisão humana e semântica de
relações permanecem abertas.
