# AstraOS Infrastructure

Containerized infrastructure for local development and future Kubernetes deployment.

## Phase 1 (default `docker compose up`)

| Service | Port | Purpose |
|---------|------|---------|
| `api` | 8000 | FastAPI gateway |
| `orchestrator` | 8001 | LangGraph control plane |
| `frontend` | 3000 | Next.js dashboard |
| `postgres` | 5432 | Persistent workflows, audit |
| `redis` | 6379 | Transient state, caching |

## Full profile (`docker compose --profile full up`)

| Service | Port | Purpose |
|---------|------|---------|
| `chroma` | 8100 | Vector DB (Phase 3) |
| `minio` | 9000/9001 | Object storage |
| `ollama` | 11434 | Local inference (Phase 7) |

## PostgreSQL

Init script: `postgres/init.sql` — extensions and helpers.

Application tables are created by SQLAlchemy on API startup (Alembic migrations in later phases).

## Networking

All services share the `astraos-net` bridge network. External access only via published ports.

## Health checks

Every application service exposes `/health` and is wired into Compose `depends_on` conditions.

## Future (Phase 6–8)

- Prometheus + Grafana configs
- OpenTelemetry collector
- RabbitMQ for event-driven execution

See [../docs/phases/README.md](../docs/phases/README.md).
