# DOCUMENT_CONVENTIONS.md

> Padrão oficial de documentação da plataforma Astera.

---

# Objetivo

Todos os documentos deverão seguir exatamente o mesmo formato.

Isso garante leitura consistente por humanos e agentes.

---

# Cabeçalho Obrigatório

```yaml
document_id:
title:
category:
status:
version:
owner:
depends_on:
used_by:
last_updated:
```

---

# Categorias Oficiais

- Product
- Architecture
- Engineering
- Runtime
- Infrastructure
- Knowledge
- ADR
- API
- Plugins
- AI
- Security

---

# Status Permitidos

- Draft
- Review
- Official
- Deprecated
- Archived

---

# Versionamento

Major.Minor

Exemplos:

- 1.0
- 1.1
- 2.0

---

# Estrutura

Todo documento deverá conter:

1. Objetivo
2. Contexto
3. Arquitetura
4. Responsabilidades
5. Fluxo
6. Princípios
7. Critérios
8. Objetivo Final

---

# Diagramas

Sempre utilizar diagramas ASCII ou Mermaid.

Nunca utilizar imagens como única fonte de informação.

---

# Linguagem

Utilizar:

- linguagem objetiva;
- frases curtas;
- termos oficiais do glossário.

---

# Alterações

Toda alteração relevante exige ADR.

---

# Objetivo Final

Padronizar toda documentação do Astera.
