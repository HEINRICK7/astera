# ASTERA FLOW — Technology Selection Policy v2

Status: **APPROVED**  
Supersedes: [Development Provider Policy v1](development-provider-policy.md)  
Authority: Astera Flow  
Scope: tecnologias do Astera, Capability Providers e Google ADK

## Objetivo

Definir como tecnologias são selecionadas dentro do Astera. A política separa
Capability Providers de Foundation Models, que possuem responsabilidades
diferentes e nunca devem ser confundidos.

## Arquitetura da plataforma

```text
Google ADK
    ↓
Foundation Model Adapter
    ↓
Cognitive Specialists
    ↓
Tools
    ↓
Astera Kernel
    ↓
Capability Layer
    ↓
Development Provider → Benchmark Provider → Production Provider
```

## Interface Desktop oficial

O Astera Connect / Astera Workbench utiliza exclusivamente:

- Deno Desktop;
- React;
- TypeScript.

Essa é uma decisão aprovada do Astera Flow. Nenhum framework ou runtime
alternativo de Desktop deve ser introduzido por conveniência. Caso uma mudança
seja necessária, ela deve ser registrada como decisão pendente e seguir o fluxo
de ADR antes de qualquer implementação.

## Duas categorias de tecnologia

### Foundation Models

São modelos usados pelo Google ADK para executar agentes: Gemini, Grok,
OpenAI, Claude, Ollama, vLLM, LM Studio ou outro compatível com o ADK.

Foundation Models **não pertencem ao Astera**. Pertencem ao runtime cognitivo
do Google ADK.

### Capability Providers

São implementações das capacidades da plataforma, como Speech, OCR, Vision,
Medical NLP, Embeddings, Terminology e FHIR. Esses providers pertencem ao
Astera e entram através de seus contratos e adapters.

## Parte I — Capability Provider Policy

Todo Capability Provider possui três perfis:

```text
Development → Benchmark → Production
```

### Development Provider

É obrigatório e deve permitir que qualquer desenvolvedor execute toda a
plataforma localmente.

Critérios obrigatórios:

- CPU First;
- Open Source;
- Docker;
- Linux;
- sem GPU ou CUDA obrigatória;
- sem dependência de Cloud ou API paga;
- inicialização rápida e baixo consumo;
- instalação e configuração simples;
- API estável, documentação oficial e comunidade ativa;
- fácil substituição;
- licença compatível.

Se qualquer critério falhar, o provider não pode ser Development Provider.

### Benchmark Provider

Existe para avaliar desempenho e qualidade. Pode usar GPU, CUDA, NVIDIA,
Triton, NIM e modelos grandes, mas nunca pode ser requisito de desenvolvimento.

### Production Provider

Só é escolhido após Benchmark, Medical Validation, CQA e Provider
Certification.

## Development Providers oficiais

| Capability | Development | Alternativa | Benchmark |
| --- | --- | --- | --- |
| Speech | faster-whisper | whisper.cpp | NVIDIA Parakeet |
| OCR | PaddleOCR | — | A definir |
| Embeddings | multilingual-e5-small | BGE Small | BGE-M3 |
| Vector Database | Qdrant | — | A definir |
| Medical NLP | spaCy → medSpaCy → Stanza | — | A definir |
| Terminology | Snowstorm | — | A definir |
| FHIR | HAPI FHIR | — | A definir |
| Database | PostgreSQL | — | A definir |
| Storage | MinIO | — | A definir |
| Event Bus | NATS | — | A definir |
| Observability | OpenTelemetry + Prometheus + Grafana + Loki | — | A definir |

## Provider Acceptance Checklist

| Critério | Obrigatório |
| --- | :---: |
| Open Source | ✅ |
| CPU | ✅ |
| Docker | ✅ |
| Linux | ✅ |
| API estável | ✅ |
| Documentação oficial | ✅ |
| Benchmark reproduzível | ✅ |
| Fácil substituição | ✅ |
| Licença compatível | ✅ |

## Parte II — Foundation Model Policy

Esta parte aplica-se exclusivamente ao Google ADK. Foundation Models não são
Capability Providers e não pertencem ao Astera.

### Interface obrigatória

O Google ADK nunca recebe seleção de modelo como acoplamento do domínio. Toda
seleção entra por um adapter de Foundation Model:

```text
FoundationModel
    ↓
GeminiAdapter / LiteLlmAdapter / OllamaAdapter / VllmAdapter
    ↓
Google ADK Agent
```

Nunca:

```text
Google ADK → Gemini específico
```

### Perfis

| Perfil | Modelos permitidos |
| --- | --- |
| Development | Gemini, Ollama, vLLM, LM Studio; Grok/OpenAI/Claude permitidos |
| Benchmark | Gemini, Grok, OpenAI, Claude, Ollama, vLLM |
| Production | configurável por organização |

O Astera não impõe um Foundation Model específico em produção.

### Responsabilidades dos agentes

Para Capability Providers:

1. Existe versão CPU?
2. É Open Source?
3. Possui Docker e documentação oficial?
4. É facilmente substituível?
5. Existe versão de Benchmark?
6. Existe estratégia de Production?

Para Foundation Models:

1. É compatível com o Google ADK?
2. Existe adapter para `FoundationModel`?
3. Está desacoplado do Kernel?
4. O ADK depende de modelo específico?
5. Pode ser substituído sem alterar o Astera?

## Princípio final

Capability Providers podem ser substituídos sem alterar Capabilities.
Foundation Models podem ser substituídos sem alterar o Google ADK ou o Kernel.
O Kernel nunca conhece providers específicos e o Google ADK nunca conhece um
Foundation Model específico fora do adapter correspondente.

Toda tecnologia entra por contratos e adapters, preservando a Arquitetura
Hexagonal, o Architecture Freeze (`ADR-010`) e a filosofia Provider-Oriented.
