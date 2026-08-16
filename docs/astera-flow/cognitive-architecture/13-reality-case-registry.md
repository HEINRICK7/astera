# 13 — Reality Case Registry

> **Superseded:** o registry canônico agora vive no [Cognitive Validation Lab](../cognitive-validation-lab/case-registry.md).
> Este documento permanece como histórico da transição de Reality Review para CQA.

| Campo | Valor |
|---|---|
| **Status** | Candidate Registry |
| **Objetivo** | Selecionar dez consultas reais para Reality Review |
| **Dados brutos no repositório** | Não permitidos nesta etapa |
| **Amostra** | Dez casos, dez especialidades/tipos de atendimento |

## Política de dados

O repositório guarda somente `case_id`, metadados, provenance, estado da
revisão, hashes autorizados e relatórios derivados. Texto clínico bruto só
pode ser acessado no ambiente e sob os termos da fonte. MIMIC exige
credenciamento e DUA; MedDialog e fontes de transcrição exigem verificação de
licença antes de qualquer cópia ou redistribuição.

## Casos candidatos

| ID | Especialidade / tipo | Fonte candidata | Foco da validação | Status |
|---|---|---|---|---|
| RR-01 | Cardiologia / dor torácica | MIMIC-IV-ED/Note | Facts → hipóteses concorrentes → exames | Candidate |
| RR-02 | Diabetes / crônica | MedDialog-EN | Perguntas de alto valor e longitudinalidade | Candidate |
| RR-03 | Pediatria | MedDialog-EN ou caso aberto | Informante familiar, idade e contexto | Candidate |
| RR-04 | Psiquiatria | MedDialog-EN ou caso aberto | Narrativa, incerteza e risco | Candidate |
| RR-05 | Obstetrícia | Caso clínico aberto | Temporalidade, gestação e contraindicações | Candidate |
| RR-06 | Dermatologia | MTSamples/MTExamples | Finding visual e limite do texto | Candidate |
| RR-07 | Ortopedia | MTSamples/MTExamples | Dor, exame físico e imagem | Candidate |
| RR-08 | Consulta de rotina | MedDialog-EN ou transcrição pública | Prevenção, ausência de queixa e plano | Candidate |
| RR-09 | Multimorbidade | MIMIC-IV-Note | Contexto grande, prioridades e conflitos | Candidate |
| RR-10 | Emergência | MIMIC-IV-ED/Note | Interrupção, ciclos rápidos e decisão | Candidate |

## Estado do registro

`Candidate` não significa que o caso já foi adquirido ou validado. Cada entrada
deve avançar por:

```text
Candidate
  → Source Verified
  → Access/License Verified
  → De-identification Verified
  → Annotated
  → Reality Reviewed
  → Medical Validation Ready
```

## Ficha de caso

```text
case_id
source_name / source_version / source_url
access_basis / license_or_dua
deidentification_basis
specialty / encounter_type
turn_count / duration_if_available
annotator / reviewer
fact_coverage
context_loss
hypothesis_naturalness
question_value
knowledge_query_timing
representation_derivation
missing_concepts
verdict
```

## Critério de seleção final

O conjunto final deve conter dez casos com material interacional suficiente e
diversidade de especialidade. Um relatório de caso publicado pode complementar
o conjunto, mas não deve ser chamado de consulta se não contiver a dinâmica de
interação necessária para avaliar interrupções, perguntas e retornos.

## Referências do registro

- [MIMIC-IV-Note](https://mimic.mit.edu/docs/IV/modules/note/)
- [MIMIC access requirements](https://mimic.mit.edu/docs/faq/how-to-get-access.html)
- [MedDialog dataset paper](https://aclanthology.org/2020.emnlp-main.743/)
- [Medical transcription sample reports](https://www.mtexamples.com/)
