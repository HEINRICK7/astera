# Case Registry

| Campo | Valor |
|---|---|
| **Status** | Candidate Registry |
| **Responsável** | Case Curator |
| **Fonte canônica anterior** | Reality Case Registry |
| **Casos registrados** | 10 |

## Objetivo

Manter o inventário dos casos usados pelo Cognitive Validation Lab, com
proveniência, especialidade, acesso, licença, desidentificação e estado de
validação.

## Casos iniciais

| ID | Especialidade / tipo | Foco CQA | Status |
|---|---|---|---|
| RR-01 | Cardiologia / dor torácica | Hipóteses concorrentes e exames | Candidate |
| RR-02 | Diabetes / crônica | Perguntas de alto valor | Candidate |
| RR-03 | Pediatria | Informante familiar e idade | Candidate |
| RR-04 | Psiquiatria | Narrativa, incerteza e risco | Candidate |
| RR-05 | Obstetrícia | Temporalidade e contraindicações | Candidate |
| RR-06 | Dermatologia | Findings e limites de texto | Candidate |
| RR-07 | Ortopedia | Exame físico e imagem | Candidate |
| RR-08 | Consulta de rotina | Prevenção e ausência de queixa | Candidate |
| RR-09 | Multimorbidade | Prioridades e conflitos | Candidate |
| RR-10 | Emergência | Interrupções e ciclos rápidos | Candidate |

## Estado do caso

```text
Candidate → Source Verified → Access Verified → De-identified Verified
          → CQA Session → Failure Analysis → Regression Candidate
          → Medical Validation Ready
```

`Candidate` não significa analisado. O Lab não armazena texto clínico bruto no
repositório; guarda identificadores, metadados, hashes autorizados e relatórios
derivados.

## Registro mínimo

```text
case_id
source / source_version / provenance
access_basis / license_or_dua
deidentification_basis
specialty / encounter_type
annotator / validator
session_ids
status
```

O registry preserva a separação entre caso de validação, resultado CQA e
decisão arquitetural.
