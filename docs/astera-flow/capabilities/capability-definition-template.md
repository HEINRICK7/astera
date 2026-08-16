# Capability Definition — Five Questions

Toda nova Capability entra no Astera Flow respondendo somente estas cinco
perguntas. Os artefatos de certificação são evidências anexas, não novas
perguntas de arquitetura.

## 1. Qual problema resolve?

Descreva o problema do usuário, o resultado esperado e o que está fora do
escopo.

## 2. Qual contrato expõe?

Identifique a entrada, a saída, invariantes, provenance e a CapabilityType.

```text
Input → Contract → Output
```

## 3. Qual provider implementa?

Liste o provider aprovado, sua versão, limitações e o Plugin que o expõe. O
provider é substituível; o contrato da capability não é definido pelo provider.

## 4. Como é validada?

Indique a evidência mínima para Engineering, Medical Validation, CQA,
Regression, Performance, Security, Observability e Documentation.

## 5. Quando pode receber Production Ready?

Defina o critério objetivo de promoção. A regra padrão é: todos os gates
obrigatórios em `PASS`, Certification Record revisado e decisão registrada no
Astera Flow.

## Regra de simplicidade

Se a Capability não puder ser explicada por essas cinco respostas, simplifique
o contrato ou divida a capability antes de criar código, SDK ou Plugin. Não
crie uma nova camada apenas para acomodar o processo.
