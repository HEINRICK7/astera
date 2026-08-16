# Capability Certification Contract

## Objetivo

Emitir um registro auditável para uma capability, separando implementação
engenheirada de readiness de produção.

O Certification Record responde à quinta pergunta da [Capability Definition —
Five Questions](capability-definition-template.md). Os gates abaixo são
evidências internas do mesmo processo, não uma nova arquitetura.

## Certification record

```text
CapabilityCertification
├── capability
├── version
├── providers
├── engineering_verdict
├── medical_validation_verdict
├── cqa_verdict
├── regression_verdict
├── performance_verdict
├── security_verdict
├── observability_verdict
├── documentation_verdict
├── evidence_refs
├── constraints
├── reviewer
├── issued_at
└── status
```

## Gates obrigatórios

| Gate | Pergunta | Evidência mínima |
|---|---|---|
| Engineering | O contrato funciona? | testes, integração, health e lifecycle |
| Medical Validation | Representa corretamente o atendimento? | relatório clínico aprovado |
| CQA | O modelo cognitivo foi representado sem perda/invenção? | validation report |
| Regression | Alterações preservaram baseline? | regression session |
| Performance | Atende SLOs definidos? | benchmark reprodutível |
| Security | Mantém controles de segurança? | security assessment |
| Observability | É operável e auditável? | traces, métricas, logs e alertas |
| Documentation | Usuário e operador conseguem usar? | documentação versionada |

## Estados

```text
Engineering Complete
→ Validation In Progress
→ Certified
→ Production Ready
```

Também são válidos `Blocked`, `Rejected`, `Expired` e `Revoked`, sempre com
motivo e referência ao Astera Flow. `Production Ready` só é válido quando todos
os gates obrigatórios são `PASS`.

## Regra de honestidade

Um teste determinístico, um provider in-memory ou um pipeline local pode provar
o contrato de Engineering, mas não pode sozinho emitir certificação clínica,
operacional ou de produção.
