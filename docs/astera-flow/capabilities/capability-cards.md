# Capability Cards

Fichas técnicas resumidas. Todos os providers listados como `Target Provider`
são intenção de integração; não significam que o engine real já esteja no
runtime.

## Speech Transcription

```yaml
Capability: Speech Transcription
Problem: Transcrever áudio clínico em texto estruturado.
Contract: SpeechTranscriber
Current Provider: DeterministicTranscriber
Target Provider: NVIDIA Parakeet
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Vision Classification

```yaml
Capability: Vision Classification
Problem: Interpretar entradas visuais clínicas dentro do contrato aprovado.
Contract: ImageAnalyzer
Current Provider: DeterministicImageAnalyzer
Target Provider: Qwen-VL (seleção real pendente)
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## OCR

```yaml
Capability: OCR
Problem: Extrair texto estruturado de documentos e imagens clínicas.
Contract: OcrEngine
Current Provider: DeterministicOcrEngine
Target Provider: Tesseract/DocTR (seleção real pendente)
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Medical NLP

```yaml
Capability: Medical NLP
Problem: Extrair entidades e assertions clínicas provider-neutral.
Contract: MedicalNlpProcessor
Current Provider: DeterministicMedicalNlp
Target Provider: MedSpaCy/Spark NLP/ClinicalBERT (seleção pendente)
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Terminology

```yaml
Capability: Medical Terminology
Problem: Resolver conceitos médicos e códigos canônicos.
Contract: TerminologyService
Current Provider: DeterministicTerminologyService
Target Provider: Snowstorm + LOINC
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## FHIR Interoperability

```yaml
Capability: FHIR Interoperability
Problem: Representar e trocar dados clínicos em HL7 FHIR.
Contract: FhirGateway
Current Provider: InMemoryFhirGateway
Target Provider: HAPI FHIR
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Embeddings

```yaml
Capability: Medical Embeddings
Problem: Gerar embeddings para recuperação de conhecimento versionada.
Contract: Embedder
Current Provider: DeterministicEmbedder
Target Provider: BGE-M3
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Clinical Facts Extraction

```yaml
Capability: Clinical Facts Extraction
Problem: Converter sinais NLP em Clinical Fact rastreável.
Contract: ClinicalFactsExtractor
Current Provider: DeterministicClinicalFactsExtractor
Target Provider: Medical NLP provider aprovado
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Clinical Context

```yaml
Capability: Clinical Context
Problem: Manter o estado clínico versionado de um encounter.
Contract: ClinicalContextBuilder
Current Provider: DeterministicClinicalContextBuilder
Target Provider: Production Context Adapter (seleção pendente)
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Clinical Reasoning

```yaml
Capability: Clinical Reasoning
Problem: Gerar hipóteses, Information Gaps e perguntas rastreáveis.
Contract: ClinicalReasoner
Current Provider: DeterministicClinicalReasoner
Target Provider: Reasoning provider aprovado
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Medical Knowledge

```yaml
Capability: Medical Knowledge
Problem: Consultar conhecimento versionado ligado a hipótese e gap.
Contract: KnowledgeRetriever
Current Provider: InMemoryKnowledgeStore + KeywordRetriever
Target Provider: Knowledge provider aprovado
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Clinical Documentation

```yaml
Capability: Clinical Documentation
Problem: Derivar SOAP, FHIR e Summary sem substituir o Context.
Contract: RepresentationEngine
Current Provider: KnowledgeRepresentationEngine
Target Provider: Production Documentation Adapter (seleção pendente)
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Clinical Consultation Core

```yaml
Capability: Clinical Consultation Core
Problem: Orquestrar a consulta do áudio à representação derivada.
Contract: CognitiveConsultationPipeline
Current Provider: Deterministic provider composition
Target Provider: Certified provider composition
Engineering: COMPLETE
Medical Validation: PENDING
CQA: PENDING
Benchmark: PENDING
Certification: NOT_ISSUED
Production: NOT_READY
```

## Vocabulário oficial

- `Specification Complete`: arquitetura e contrato aprovados.
- `Engineering Complete`: código e testes de contrato concluídos.
- `Deterministic Provider`: apenas adapter/mock determinístico em uso.
- `Real Provider Pending`: engine real ainda não integrado ou não validado.
- `Capability Certified`: todos os gates aprovados.
- `Production Ready`: certificação emitida pelo Astera Flow.
