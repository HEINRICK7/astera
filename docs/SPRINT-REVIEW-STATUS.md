# Sprint Review — Estado real do Astera

**Data da revisão:** 08/08/2026  
**Escopo:** comunicação, Speech Runtime, extração clínica, Knowledge Layer, A2UI e jornada clínica.

## Resposta direta

Hoje o Astera já consegue:

- conectar notebook e smartphone pelo Galène;
- transmitir áudio e vídeo em uma consulta;
- capturar o áudio remoto no Workbench;
- enviar o áudio para o Speech Runtime;
- extrair fatos clínicos rapidamente;
- construir uma projeção versionada do Clinical Graph;
- publicar cards e timeline por A2UI JSONL;
- atualizar o mesmo card incrementalmente;
- executar o pipeline profundo de contexto, raciocínio e representação SOAP;
- concluir a jornada de revisão com SOAP, FHIR e persistência.

Isso não significa que todos esses pontos estejam certificados em produção. A tabela abaixo separa implementação, validação automatizada e demonstração real.

## Antes e agora

| Capacidade | Antes | Agora | Estado real |
|---|---|---|---|
| Vídeo notebook ↔ smartphone | Apenas tela de vídeo | Chamada WebRTC funcional pelo Galène | **Validado manualmente** |
| Áudio da consulta | Não alimentava o Runtime ao vivo | Áudio remoto capturado pelo Workbench e enviado em PCM | **Implementado; validado em sessão local** |
| Realtime Layer | Inexistente na UI | RMS, peak, speaking, silêncio e qualidade | **Implementado** |
| Speech Runtime | Sem fluxo clínico ao vivo | Stream de áudio para transcrição incremental | **Implementado; precisa de validação de latência** |
| Clinical Extraction | Sem fatos no fluxo ao vivo | Extrator rápido por palavras-chave e adaptador Grok | **Implementado e testado** |
| Clinical Graph | Não era fonte de apresentação | Facts entram no `ClinicalGraphBuilder` | **Implementado e testado** |
| Knowledge Layer | Cards eram alimentados diretamente | Projeção versionada com fatos, grafo, eventos e timeline | **Implementado e testado** |
| Clinical Cards | Resultado aparecia sem evolução declarativa | `create` → `patch` → `validate` no mesmo id | **Implementado e testado** |
| Knowledge Timeline | Não existia | Timeline derivada dos eventos do Knowledge Layer | **Implementado e integrado** |
| A2UI Cognitive Stream | Não existia no live stream | JSONL com operações declarativas | **Implementado e testado** |
| Component Registry | Parcial | Cards e timeline registrados no Design System | **Implementado; build validado** |
| Deep Pipeline | Não estava separado do caminho rápido | Contexto, raciocínio e SOAP executados de forma assíncrona | **Implementado e testado com reasoner determinístico** |
| SOAP | Disponível somente na jornada processada | Evento SOAP também é emitido no pipeline profundo | **Implementado; sessão real ainda requer validação ponta a ponta** |
| Encerramento | Não havia consolidação completa | Jornada possui SOAP, FHIR e persistência | **Implementado e testado** |

## O que já foi comprovado sem depender de interpretação visual

### Comunicação

Foi realizada a validação local entre notebook e smartphone. O vídeo remoto chegou ao Workbench, o preview local apareceu no smartphone e o áudio remoto foi disponibilizado para o pipeline clínico.

O Runtime HTTPS está ativo e respondendo:

```text
GET https://127.0.0.1:8001/health
{"status":"alive"}
```

### Pipeline rápido

O pipeline de baixa latência não espera o raciocínio profundo para publicar conhecimento básico:

```text
áudio
  → Speech Runtime
  → Clinical Extraction
  → Clinical Knowledge
  → A2UI Cognitive Stream
  → Clinical Cards
```

O teste automatizado confirma que o evento `a2ui.cognitive.stream` é publicado antes do evento de raciocínio profundo.

### Clinical Graph e Knowledge Layer

Cada fato clínico recebido gera uma projeção que contém:

- versão do conhecimento;
- fatos clínicos;
- grafo clínico;
- cards derivados do grafo;
- eventos de conhecimento;
- timeline de evolução.

A UI não recebe mais uma transcrição para decidir o que desenhar. Ela recebe a representação declarativa produzida pelo Knowledge Layer.

### A2UI

O fluxo incremental validado é:

```jsonl
{"op":"create","component":"ClinicalCard","id":"..."}
{"op":"create","component":"KnowledgeTimeline","id":"knowledge-timeline"}
{"op":"patch","id":"...","patch":{...}}
{"op":"patch","id":"knowledge-timeline","patch":{...}}
{"op":"validate","id":"..."}
```

O renderer mantém o mesmo nó em memória. Uma atualização não recria o card; ela altera suas propriedades e seu estado.

## Evidências de validação executadas

```text
Runtime — testes focados: 3 passed
Runtime — testes adicionais: 5 passed
Workbench — npm run build: concluído com sucesso
Runtime HTTPS: serviço ativo
Health check: alive
```

Os testes cobrem especificamente:

- projeção do Knowledge Layer;
- operações A2UI incrementais;
- criação da Knowledge Timeline;
- ordem Fast Pipeline antes do Deep Pipeline;
- publicação do protocolo `a2ui-cpp/1`.

## O que ainda não pode ser chamado de concluído

### Latência clínica

O fluxo rápido está implementado, mas ainda não existe uma medição formal e repetível comprovando a meta de menos de um segundo em diferentes dispositivos e condições de rede.

### Grok em sessão real

O adaptador Grok e o raciocínio profundo existem no Runtime. A validação automatizada usa um reasoner determinístico. A estabilidade do Grok real, incluindo retorno de entidades e latência, ainda precisa de uma rodada própria de certificação.

### SOAP ao encerrar uma chamada WebRTC

SOAP, FHIR e persistência estão comprovados na jornada processada. Ainda falta comprovar que o encerramento da chamada WebRTC real dispara automaticamente a consolidação completa sem intervenção adicional.

### Replay e auditoria do conhecimento

O estado é versionado e a timeline é registrada. Ainda não existe uma interface final de Time Machine, replay visual da consulta ou auditoria completa de undo/redo para o médico.

### Multiplataforma nativa

O protocolo foi isolado para permitir outros renderers. Desktop/Web/Mobile nativos consumindo o mesmo stream ainda não foram entregues como implementações independentes.

## Conclusão

O salto implementado é real: o Astera deixou de ser apenas uma chamada Galène com uma tela clínica e passou a possuir um caminho funcional de áudio → extração → grafo → conhecimento → A2UI.

O que está comprovado hoje é uma **base funcional local**, com testes automatizados e uma integração real notebook ↔ smartphone. O que ainda falta é transformar essa base em uma demonstração ponta a ponta repetível, com latência medida, Grok real estável e SOAP automático ao encerrar a consulta.

**Status honesto da Sprint:** base arquitetural implementada; comunicação validada; pipeline clínico funcional em desenvolvimento local; certificação ponta a ponta ainda pendente.
