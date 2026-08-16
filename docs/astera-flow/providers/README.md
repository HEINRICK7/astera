# Providers

| Campo | Valor |
|---|---|
| **Status** | Active |
| **Responsabilidade** | Implementar Capability sem alterar seus contratos |
| **Evaluation** | Astera Benchmark Lab |
| **Promotion** | Provider Benchmark → Validation → Certification |

## Provider lifecycle

```text
Draft → Implemented → Engineering Approved → Benchmarked
      → Medical Validated → CQA Approved → Certified
      → Production Ready → Deprecated → Retired
```

Providers são substituíveis. O provider determinístico é usado para contract
tests; o Development Provider oficial mantém o desenvolvimento local sem GPU.
Providers de Benchmark e Production precisam de versão, ambiente, licença,
benchmark, proveniência e evidências operacionais próprias.

## Profiles

| Capability | Development Provider | Benchmark Provider | Production |
|---|---|---|---|
| Speech | faster-whisper | NVIDIA Parakeet NIM | Not certified |
| OCR | PaddleOCR | Pending | Not certified |
| Embeddings | multilingual-e5-small | BGE-M3 | Not certified |
| Terminology | Snowstorm | Pending | Not certified |
| FHIR | HAPI FHIR | Pending | Not certified |

The governing document is the approved
[Development Provider Policy](../development-provider-policy.md).

## Foundation Models are separate

Gemini, Grok, OpenAI, Claude, Ollama, vLLM e LM Studio são Foundation Models
do runtime Google ADK, não Capability Providers do Astera. Eles entram no ADK
por adapters como `GeminiAdapter` ou `LiteLlmAdapter`.

Consulte a [Technology Selection Policy v2](../technology-selection-policy-v2.md).

## Provider matrix

| Capability | Current adapter | Target/approved provider | State |
|---|---|---|---|
| Speech | FasterWhisperTranscriber (development) | NVIDIA Parakeet NIM (benchmark) | Development approved · Benchmark pending |
| Vision | DeterministicImageAnalyzer | Qwen-VL candidate | Selection/Integration Pending |
| OCR | DeterministicOcrEngine | Tesseract/DocTR candidate | Selection/Integration Pending |
| Medical NLP | DeterministicMedicalNlp | MedSpaCy/Spark NLP/ClinicalBERT candidate | Selection/Integration Pending |
| Terminology | DeterministicTerminologyService | Snowstorm + LOINC | Real Provider Pending |
| FHIR | InMemoryFhirGateway | HAPI FHIR | Real Provider Pending |
| Embeddings | DeterministicEmbedder | BGE-M3 | Real Provider Pending |

## Regra de integração

Provider code MUST depend on the port and SDK. Capability code MUST NOT depend
on provider-specific APIs, response objects or configuration names. Development
must not require the Benchmark Provider.

Speech remains the first provider readiness review:
[Speech Provider Readiness Checklist](../capabilities/speech-provider-readiness.md).

Sprint 1 reports:
[Parakeet Integration Report](parakeet-integration-report.md) ·
[Parakeet Readiness Report](parakeet-readiness-report.md).

O contrato de lifecycle, os gates e o primeiro candidato estão em
[Provider Certification](provider-certification.md).
