# Foundation Model Benchmark

Benchmark de Foundation Models pertence ao runtime Google ADK e é separado do
Benchmark de Capability Providers.

## Protocolo

```text
Mesmo caso clínico
    ↓
Foundation Model Adapter
    ↓
Google ADK
    ↓
Mesmos Specialists e Tools
    ↓
SOAP / FHIR / Knowledge
    ↓
Comparação
```

Modelos comparados podem incluir Gemini, Grok, OpenAI, Claude, Ollama e vLLM,
desde que entrem pelo mesmo boundary de Foundation Model.

## Métricas

- fidelidade ao Clinical Context;
- perda e criação de informação;
- coerência das hipóteses;
- qualidade das perguntas e Information Gaps;
- qualidade de SOAP/FHIR;
- latência, custo e tokens;
- estabilidade de tool calling;
- CQA e Medical Validation.

Um resultado de benchmark não autoriza uso em produção. O dataset precisa ser
versionado, autorizado e igual para todos os modelos.
