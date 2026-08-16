# Capability Catalog

O Capability Catalog é a visão provider-neutral que o Google ADK e a
orquestração podem consultar para descobrir o que o Astera oferece.

```text
ADK → Capability Catalog → Capability → Contract
                                  └── Provider Adapter
```

O catálogo expõe apenas:

- nome da Capability;
- providers disponíveis;
- número de providers saudáveis.

Ele não expõe endpoints, classes, payloads ou detalhes específicos de um
provider. A implementação está em `CapabilityCatalog` e lê o registro já
existente; não cria uma segunda fonte de verdade.

## Exemplo

```json
[
  {
    "capability": "speech.transcription",
    "providers": ["speech"],
    "healthy_providers": 1
  }
]
```

## Invariantes

- O ADK não conhece provider específico.
- O catálogo não escolhe provider; a seleção continua no Registry/Scorer.
- O Kernel não conhece API de provider.
- A ausência de provider saudável é reportada, não mascarada.
