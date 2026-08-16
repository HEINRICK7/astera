---
document_id: astera-clinical-workflow-dataset
title: Clinical Workflow Dataset
category: Product
status: Official
version: 1.1
owner: Astera Clinical Validation
depends_on:
  - ../product-backlog.md
  - README.md
used_by:
  - Clinical Product Increments
  - Provider Comparison
  - Demo Day
last_updated: 2026-08-07
---

# Clinical Workflow Dataset

O Clinical Workflow Dataset mede a jornada clínica completa. Ele não substitui
benchmarks de providers; ele verifica se o produto preserva informação e gera
uma saída revisável ao longo de um atendimento.

## Princípio do dataset

O item de avaliação é um workflow clínico completo, não uma frase de teste de
Speech. O mesmo caso deve atravessar todos os estágios para que o Astera possa
comparar providers e modelos pelo resultado final:

\`\`\`text
Golden Consultation
  ↓
Transcript → Clinical Facts → Context → Reasoning → Knowledge
  ↓
SOAP → FHIR → Persistence → Clinical Replay
\`\`\`

Benchmarks isolados continuam existindo como evidência técnica, mas nunca
substituem este dataset de produto.

## Versionamento e registry

| Versão | Estado | Casos | Observação |
|---|---|---:|---|
| v1.1 | 🟡 Em preparação | 1 planejado | Roteiro definido; gravação autorizada ainda pendente |

O registry de cada caso deve conter apenas metadados não sensíveis:

| Campo | Obrigatório | Regra |
|---|---|---|
| case_id | Sim | ID estável, por exemplo GC-001 |
| workflow | Sim | Primary Care, Pediatrics, Psychiatry etc. |
| language | Sim | pt-BR no primeiro caso |
| audio_hash | Quando houver áudio | Hash do artefato armazenado com segurança |
| consent_reference | Quando houver pessoa real | Referência à autorização, nunca o documento no Git |
| expected_outputs | Sim | Facts, lacunas, SOAP e FHIR esperados |
| status | Sim | Planned, Recorded, Evaluated ou Certified |

Áudios, transcrições identificáveis e documentos clínicos não devem ser
commitados. O dataset de desenvolvimento deve usar gravação autorizada,
simulada ou devidamente desidentificada, conforme aprovação aplicável.

Dados clínicos reais não devem ser commitados. O registry deve armazenar apenas
IDs, consentimento/autorização, hashes, metadados não sensíveis e localização
segura do artefato.

## Golden Consultation 001 — Consulta Primária

**Caso:** adulto em atenção primária com dor torácica e fatores de risco.  
**Especialidade:** Primary Care / Cardiology screening.  
**Entrada:** gravação de voz autorizada, em português brasileiro.  
**Estado:** roteiro definido; gravação autorizada pendente.

### Roteiro de gravação

O áudio deve ser gravado por uma pessoa autorizada, com fala natural e sem
intervenção do operador durante a execução:

> Bom dia doutor. Estou com dor no peito há três dias. A dor piora quando faço
> esforço. Tenho diabetes e pressão alta. Estou tomando Losartana. Não tenho
> alergia conhecida.

Este texto é roteiro de validação, não um áudio clínico e não deve ser tratado
como evidência até que uma gravação autorizada seja registrada.

### Evidências esperadas

| Etapa | Evidência mínima |
|---|---|
| Transcript | Texto, idioma, segmentos, timestamps e request_id |
| Clinical Facts | Dor torácica, piora ao esforço, diabetes, hipertensão, losartana, ausência de alergia conhecida |
| Clinical Context | Facts relacionados e timeline do encontro |
| Reasoning | Hipóteses e lacunas sem diagnóstico automático conclusivo |
| Knowledge | Consultas motivadas pelas lacunas/hipóteses |
| SOAP | Documento derivado e revisável |
| FHIR | Representação do encontro e documentação |
| Persistência | Artefatos duráveis e recuperáveis |
| Replay | Jornada completa navegável |

### Clinical Facts esperados

| Tipo | Conteúdo esperado | Regra de avaliação |
|---|---|---|
| Queixa | Dor no peito | Deve permanecer atribuída ao paciente |
| Duração | Há três dias | Não converter em data absoluta sem evidência |
| Fator de piora | Piora ao esforço | Deve ser preservado no Context |
| Condição prévia | Diabetes | Fato relatado; não inferir controle |
| Condição prévia | Hipertensão | Fato relatado; não inferir gravidade |
| Medicação | Losartana | Não inventar dose, frequência ou adesão |
| Alergia | Nega alergia conhecida | Registrar como relato negativo, não como risco zero |

### Lacunas que devem permanecer explícitas

O sistema não deve inventar idade, sexo, intensidade ou caráter da dor,
irradiação, sintomas associados, sinais vitais, exame físico, exames
complementares, diagnóstico ou plano terapêutico. Esses itens podem ser
perguntados ou exibidos como lacunas para revisão médica.

### Regras de comparação

- o mesmo caso deve poder ser executado com diferentes Speech Providers;
- diferenças de provider devem ser observadas via evidência, não misturadas ao
  domínio clínico;
- transcript, Facts, Context, hipóteses, SOAP e FHIR devem possuir diffs;
- informação inventada, perdida ou não rastreável gera falha do CPI;
- nenhum caso recebe status Certified antes de Medical Validation e CQA.

## Protocolo de comparação entre providers

1. Executar o mesmo áudio e a mesma versão do caso com cada provider.
2. Armazenar provider, versão, timestamp e evidências no evidence path.
3. Normalizar apenas o envelope técnico; não normalizar silenciosamente o
   conteúdo clínico divergente.
4. Comparar Transcript, Facts, Context, hipóteses, SOAP e FHIR por diffs.
5. Registrar perdas, invenções, omissões e necessidade de correção médica.

Métricas mínimas por execução:

| Métrica | Definição |
|---|---|
| Workflow completion rate | Consultas que chegam à persistência / consultas iniciadas |
| Critical fact recall | Fatos críticos presentes na saída / fatos críticos esperados |
| Unsupported content rate | Afirmações sem evidência / afirmações clínicas avaliadas |
| SOAP acceptance rate | SOAP aceito pelo médico com poucas correções / SOAP revisados |
| FHIR validity rate | Representações válidas e recuperáveis / representações geradas |

Nenhuma meta numérica vira certificação sem método de amostragem e aprovação
clínica. O dashboard deve mostrar N/A quando a amostra ainda não existir.

## Próximos casos

| ID | Caso | Estado |
|---|---|---|
| Golden Consultation 002 | Pediatria | Planned |
| Golden Consultation 003 | Psiquiatria | Planned |
| Golden Consultation 004 | Dermatologia | Planned |
| Golden Consultation 005 | Consulta de retorno | Planned |
| Golden Consultation 006 | Emergência | Planned |
