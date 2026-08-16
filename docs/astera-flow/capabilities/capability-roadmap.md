# Capability Status Board

Atualizado em **2026-08-07**. Percentuais não são preenchidos sem medição
reprodutível; o board registra o estado real de cada gate.

| Capability | Engineering | Medical Validation | CQA | Regression | Certification | Production |
|---|---|---|---|---|---|---|
| Speech Transcription | PASS | NOT RUN | NOT RUN | NOT RUN | NOT ISSUED | NOT READY |
| Clinical Facts Extraction | PASS | NOT RUN | NOT RUN | NOT RUN | NOT ISSUED | NOT READY |
| Clinical Context | PASS | NOT RUN | NOT RUN | NOT RUN | NOT ISSUED | NOT READY |
| Clinical Reasoning | PASS | NOT RUN | NOT RUN | NOT RUN | NOT ISSUED | NOT READY |
| Medical Knowledge | PASS | NOT RUN | NOT RUN | NOT RUN | NOT ISSUED | NOT READY |
| Clinical Documentation | PASS | NOT RUN | NOT RUN | NOT RUN | NOT ISSUED | NOT READY |
| Clinical Consultation Core | PASS | NOT RUN | NOT RUN | NOT RUN | NOT ISSUED | NOT READY |

## Evidência de Engineering

O estado `PASS` representa contratos, lifecycle de Plugin, capability/provider
registration, health e testes automatizados existentes. Não representa
aprovação clínica ou readiness operacional.

## Classificação atual

As capabilities listadas possuem, conforme evidência no repositório:

| Classificação | Estado atual |
|---|---|
| Specification Complete | Sim — contratos aprovados |
| Engineering Complete | Sim — código e testes de contrato |
| Deterministic Provider | Sim — adapter local usado nos testes |
| Real Provider Pending | Sim — engines reais ainda não integrados/validados |
| Capability Certified | Não emitida |
| Production Ready | Não emitida |

Os detalhes por capability estão nas [Capability Cards](capability-cards.md).

| Capability | Principais evidências |
|---|---|
| Speech Transcription | `speech_sdk`, `SpeechPlugin`, `test_speech_plugin.py` |
| Clinical Facts Extraction | `clinical_facts_sdk`, `ClinicalFactsPlugin`, testes de provenance/polarity |
| Clinical Context | `clinical_context_sdk`, versionamento e timeline |
| Clinical Reasoning | `reasoning_sdk`, hipóteses, gaps e questions |
| Medical Knowledge | `medical_knowledge_sdk`, query ligada a hipótese/gap |
| Clinical Documentation | `representation_sdk`, SOAP/FHIR/Summary com context provenance |
| Clinical Consultation Core | `CognitiveConsultationPipeline`, teste end-to-end |

## Próxima execução

Capability Zero: iniciar a sessão de certificação de `Speech Transcription`:

```text
Speech → Benchmark → Medical Validation → CQA → Regression
       → Performance → Security → Observability → Documentation
       → Certification Review
```
