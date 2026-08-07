# Documentação da Infraestrutura - Fase B

Esta documentação descreve a configuração dos serviços auxiliares e de persistência no Docker Compose, validada através de Health Checks.

## Serviços Configurados

- **PostgreSQL**: Porta `5433` mapeada (host). Usuário `astera_user`. Healthcheck via `pg_isready`. (Banco principal e Langfuse).
- **Redis**: Porta `6380` (host). Healthcheck via `redis-cli ping`. (Cache/Filas para Langfuse e Workers).
- **NATS (com JetStream)**: Portas `4222` e `8222` (Management/Health). Healthcheck via chamada HTTP local ao management server.
- **Qdrant**: Portas `6333` e `6334`. Armazenamento vetorial. (S/ healthcheck embutido devido a falta de ferramentas de rede na imagem alpine).
- **MinIO**: Portas `9002` (API) e `9003` (Console). Credenciais: `astera_admin`/`astera_minio_password`. Healthcheck nativo (`/minio/health/live`).
- **OpenTelemetry Collector**: Portas `4317` (gRPC), `4318` (HTTP), `8889` (Prometheus metrics). Recebe telemetria e roteia.
- **Prometheus**: Porta `9091`. Scrape metrics do OpenTelemetry Collector.
- **Loki**: Porta `3100`. Armazenamento de logs.
- **Grafana**: Porta `3001`. Provisionado com datasources para Loki e Prometheus.
- **Langfuse**: Porta `3002`. Conectado ao PostgreSQL e Redis. Plataforma de observabilidade de LLMs.

## Validação de Health Checks
Todos os serviços configurados com Health Checks (Postgres, Redis, NATS, MinIO) foram validados através do comando `docker inspect` e estão com o status `healthy`. Os outros serviços (Prometheus, Loki, Grafana, Langfuse, OTel) foram confirmados como ativos sem reinicializações constantes (`Up`).

## Contratos Pydantic
Criados contratos robustos em:
- `packages/shared/events/events.py`: Modelos-base e eventos padrão (`WorkflowStartedEvent`, `StepCompletedEvent`, etc.) para uso em comunicação async.
- `packages/contracts/api.py`: Schemas de Requisição e Resposta para a API (ex: `CreateWorkflowRequest`, `ExecutionStatusResponse`).
