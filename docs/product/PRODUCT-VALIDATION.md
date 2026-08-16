# ASTERA — PRODUCT VALIDATION

Status: `PENDING VALIDATION`

Architecture baseline: `READY`

## Objetivo

Validar o comportamento do produto em cenários clínicos representativos,
usando a arquitetura Runtime já consolidada.

Esta fase não reorganiza pipelines, não cria uma segunda fonte de verdade e
não abre uma nova sprint arquitetural. Ela mede se o produto entrega a
experiência clínica esperada.

## Golden Audio

O primeiro cenário deve conter, em uma consulta coerente:

```text
Paciente
  ↓
Dor torácica
  ↓
Hipertensão
  ↓
Medicamentos
  ↓
Alergias
  ↓
Exames
  ↓
Condutas
```

Sequência esperada:

```text
Speech Runtime
  ↓
StreamingTranscriptState
  ↓
Clinical Runtime
  ↓
Knowledge Runtime
  ↓
Presentation Runtime
  ↓
A2UI Runtime
  ↓
RuntimeSessionProjection
  ↓
Clinical Experience
```

## Matriz de cenários

| ID | Cenário | Resultado esperado | Status |
|---|---|---|---|
| PV-001 | Golden Audio clínico | Facts, Knowledge, Presentation, A2UI e Projection completos | PENDING |
| PV-002 | Consulta completa | sessão inicia, processa e finaliza sem perda de estado | PENDING |
| PV-003 | Áudio ruim | degradação explícita, sem estado clínico inventado | PENDING |
| PV-004 | Áudio longo | transcript incremental e projeção estável | PENDING |
| PV-005 | Consulta interrompida | encerramento consistente e sessão recuperável | PENDING |
| PV-006 | Troca de paciente | isolamento completo entre sessões | PENDING |
| PV-007 | Evidence Engine | PDF, imagem, WhatsApp, exames e FHIR entram pela sessão oficial | PENDING |
| PV-008 | Clinical Experience | médico visualiza uma experiência coerente e acionável | PENDING |
| PV-009 | Desktop | alvo oficial compila e executa o Runtime | PENDING — infraestrutura |

## Registro obrigatório por cenário

Cada execução deve registrar:

- identificador da sessão;
- provider de Speech utilizado;
- eventos emitidos e ordem;
- transcript final e parciais relevantes;
- facts detectados;
- knowledge retornado;
- Presentation e A2UI gerados;
- estado final da `RuntimeSessionProjection`;
- tela e renderer que consumiram a projeção;
- erros, latência e perda de eventos;
- decisão `PASS` ou `FAIL`.

## Critérios de aprovação

Um cenário passa quando:

1. percorre o Runtime oficial;
2. não cria caminho paralelo para React;
3. apresenta dados clínicos coerentes com o áudio;
4. mantém isolamento entre sessões;
5. registra evidência reproduzível.

Falha funcional deve gerar correção de produto ou provider. Não deve gerar
uma nova pipeline paralela. Mudança arquitetural só pode ocorrer mediante ADR
aprovado.

## Roadmap de produto

1. Speech Runtime — qualidade e robustez da transcrição;
2. Clinical Experience — experiência premium para o médico;
3. Evidence Engine — documentos, imagens, WhatsApp, exames e FHIR;
4. Reasoning Engine — hipóteses e raciocínio clínico;
5. Clinical Copilot.

O baseline arquitetural permanece congelado enquanto esta validação avança.
