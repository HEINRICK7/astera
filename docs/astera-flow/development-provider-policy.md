# ASTERA FLOW — Development Provider Policy v1 (superseded)

Status: **SUPERSEDED**  
Version: 1.0  
Authority: Astera Flow  
Scope: Platform, Capabilities, Providers e ambientes de desenvolvimento

Esta política foi substituída pela [Technology Selection Policy v2](technology-selection-policy-v2.md),
que separa Capability Providers de Foundation Models do Google ADK.

## Objetivo

O Astera é uma plataforma Provider-Oriented, mas seu desenvolvimento nunca
pode depender de GPU, cloud provider, CUDA, APIs pagas ou infraestrutura
complexa. Toda Capability deve possuir um Development Provider que permita
desenvolver, testar, validar e executar CI localmente em CPU.

## Perfis de provider

```text
Development Provider → Benchmark Provider → Production Provider
```

| Perfil | Objetivo | GPU/cloud permitido |
| --- | --- | --- |
| Development | desenvolvimento, testes, pipelines, consultas e CI | Não |
| Benchmark | comparação de providers e desempenho | Sim |
| Production | operação certificada | Somente após os gates aprovados |

## Critérios obrigatórios do Development Provider

Todos os critérios precisam ser atendidos:

- CPU First, sem NVIDIA GPU ou CUDA obrigatórios;
- 100% Open Source e licença compatível com uso comercial;
- Docker oficial ou Docker fácil de construir;
- sem cloud obrigatória, API paga ou serviço externo obrigatório;
- inicialização, instalação e configuração rápidas;
- Linux e notebook comum;
- API simples, documentação oficial e comunidade ativa;
- substituição fácil por outro provider.

Se qualquer resposta for negativa, o provider não pode ser Development
Provider sem uma exceção tecnicamente justificada e aprovada pelo Astera Flow.

## Acceptance Criteria

| Critério | Obrigatório |
| --- | :---: |
| Open Source | ✅ |
| CPU | ✅ |
| Docker | ✅ |
| Linux | ✅ |
| API estável | ✅ |
| Documentação oficial | ✅ |
| Comunidade ativa | ✅ |
| Benchmark reproduzível | ✅ |
| Licença compatível | ✅ |
| Fácil substituição | ✅ |

## Development Providers oficiais

| Capability | Development Provider | Alternativa | Status |
| --- | --- | --- | --- |
| Speech | faster-whisper | whisper.cpp | Approved |
| OCR | PaddleOCR | — | Approved |
| Embeddings | multilingual-e5-small | BGE Small | Approved |
| Vector Database | Qdrant | — | Approved |
| Medical NLP | spaCy → medSpaCy → Stanza | — | Approved |
| Terminology | Snowstorm | — | Approved |
| FHIR | HAPI FHIR | — | Approved |
| Database | PostgreSQL | — | Approved |
| Storage | MinIO | — | Approved |
| Event Bus | NATS | — | Approved |
| Observability | OpenTelemetry + Prometheus + Grafana + Loki | — | Approved |

## Providers de Benchmark e Production

NVIDIA NIM, Parakeet, Azure AI, Vertex AI, AWS Bedrock, OpenAI API, Deepgram,
AssemblyAI, Gemini, Claude e qualquer provider pago, cloud-only ou GPU-only
pertencem exclusivamente aos perfis Benchmark ou Production.

Parakeet continua sendo pesquisado no [Astera Research](../../labs/astera-research/README.md)
como Benchmark Provider. Sua pesquisa não pode bloquear desenvolvimento local.

## Architecture Rule

Nenhuma Capability conhece seu provider:

```text
Capability → Contract → Provider Adapter → Provider
```

O ProviderTrace, latência, GPU, retries e diagnósticos permanecem na camada de
infraestrutura/evidência e não vazam para o domínio clínico.

## Ordem obrigatória

```text
Pesquisa → Development Provider → Integração → Testes
         → Benchmark Provider → Medical Validation
         → Provider Certification → Production Provider
```

Um provider só pode ser aceito quando houver evidência de que roda em CPU,
Docker e Linux, pode ser usado por qualquer desenvolvedor, mantém contratos,
não altera Kernel/SDKs/Capabilities e preserva a arquitetura congelada.

## Responsabilidade dos agentes

Antes de adotar qualquer provider, o agente deve responder:

1. Qual é o Development Provider?
2. Ele atende todos os critérios desta política?
3. Existe Docker?
4. Funciona em CPU?
5. É Open Source?
6. Existe documentação oficial?
7. É facilmente substituível?

Qualquer resposta negativa exige justificativa técnica e aprovação antes da
continuação.

## Regra de ouro

Qualquer desenvolvedor deve conseguir subir o projeto, executar testes,
pipelines, consultas, integrações e CI em um notebook comum, utilizando apenas
software Open Source, Docker e CPU. GPU, cloud e modelos de alta performance
são opcionais para Benchmark e Production, nunca para Development.
