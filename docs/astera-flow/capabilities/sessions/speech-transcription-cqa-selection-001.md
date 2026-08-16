# Speech Transcription — CQA Case Selection 001

| Campo | Valor |
|---|---|
| **Session** | `speech-transcription-cqa-selection-001` |
| **Capability** | `speech.transcription` |
| **Status** | Ready |
| **Raw clinical data** | Não armazenado no repositório |
| **CQA verdict** | Not Run |

## Objetivo

Selecionar casos e corpus que possam avaliar Speech Transcription sem confundir
validação textual do Cognitive Model com validação acústica do provider.

## Separação de evidências

| Trilha | O que valida | Entrada exigida |
|---|---|---|
| Speech benchmark | latência, erro, idioma e transcript | áudio autorizado + referência |
| Cognitive CQA | Facts, Context, Reasoning e Documentation | caso clínico + anotação de referência |
| Medical Validation | fidelidade clínica do resultado | relatório e revisor habilitado |

Os dez casos do Case Registry são candidatos à CQA cognitiva. Eles não são
automaticamente corpus de Speech: cada caso precisa de áudio, licença,
proveniência e base de desidentificação verificadas.

## Critérios de entrada

- `Source Verified`;
- `Access Verified`;
- `De-identified Verified`;
- formato de áudio e referência textual disponíveis para benchmark;
- idioma e especialidade registrados;
- hash do artefato autorizado;
- nenhum conteúdo clínico bruto persistido no repositório.

## Estado atual

Nenhum caso foi promovido nesta sessão. O próximo agente de CQA deve preencher
somente metadados autorizados, executar a comparação e produzir Validation
Report. A seleção não emite Medical Validation nem Certification.

## Próxima saída

`SpeechCqaReport` com transcript fidelity, information loss, invented
information, provenance, provider/version e decisão de Regression Candidate.
