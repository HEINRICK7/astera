# RFC-003 — Estratégia Oficial para Geração e Validação FHIR

| Campo | Valor |
|---|---|
| Status | Proposed |
| Owner | Astera Architecture |
| Priority | High |
| Impact | Clinical Graph → FHIR |
| Reference provider | HAPI FHIR |

## Decisão proposta

O Astera é responsável por interpretar o Clinical Graph, decidir quais
recursos clínicos devem existir, relacioná-los, preservar proveniência e
produzir um Bundle FHIR. O Astera não reimplementa o padrão FHIR.

HAPI FHIR será responsável pela validação especializada do Bundle e dos
recursos: tipos, cardinalidade, referências, perfis e terminologias quando
configuradas. HAPI não gera o Bundle, porque não conhece o domínio clínico do
Astera.

```text
Clinical Graph
    ↓
Astera FHIR Mapper
    ↓
FHIR Bundle
    ↓
HAPI FHIR Validator
    ↓
Validated Bundle
    ↓
Persistence / Export / API
```

## Fronteiras

### Astera

- `Condition` → `Condition`;
- `Medication` → `MedicationStatement` ou recurso aprovado pela revisão;
- `Observation` → `Observation`;
- `Allergy` → `AllergyIntolerance`;
- `Procedure`/`Exam` → `Procedure` e/ou `DiagnosticReport` conforme domínio;
- `Encounter` e `Patient`;
- referências entre recursos;
- proveniência e rastreabilidade até Clinical Fact/Transcript;
- composição do Bundle.

### HAPI FHIR

- validação de instância e Bundle;
- conformidade com perfis;
- cardinalidade e tipos FHIR;
- referências e terminologias configuradas;
- persistência/repositório HAPI quando o ambiente for aprovado.

O Astera não deve implementar parser, serializer, validator ou regras completas
da especificação FHIR em paralelo ao HAPI.

## Estado encontrado no Runtime

O Runtime atual possui `FhirResource`, `FhirBundle`, `FhirGateway` e
`InMemoryFhirGateway` para contratos e testes locais. A validação atual é
deliberadamente mínima. O CPI-001 ainda produz uma representação FHIR local e
não possui um FHIR Mapper baseado no Clinical Graph nem validação HAPI.

Essa diferença é uma lacuna registrada, não uma falha a ser escondida por uma
implementação manual maior.

## Roadmap proposto

1. FHIR Mapper a partir do Clinical Graph.
2. Bundle Builder do Astera.
3. Adapter HAPI Validator.
4. Validação de Bundle com erros estruturados.
5. Persistência HAPI.
6. Perfis clínicos e terminologias.

Nenhum item acima está autorizado por este documento enquanto o RFC estiver
`Proposed`.

## Gates de aprovação

- [ ] Clinical Graph aprovado como representação canônica.
- [ ] Catálogo de mapeamentos Node → FHIR validado clinicamente.
- [ ] Proveniência e referências entre recursos definidas.
- [ ] Bundle mínimo da Golden Consultation 001 revisado.
- [ ] HAPI Validator escolhido/configurado no ambiente aprovado.
- [ ] Erros de validação retornados sem alterar contratos públicos.
- [ ] ADR e aprovação do Astera Flow registradas.

## Não escopo

Este RFC não altera Kernel, ADK, Providers de Foundation Model, contratos
públicos, Clinical Graph atual ou o pipeline CPI-001. Não adiciona Docker,
servidor HAPI ou persistência externa nesta etapa.
