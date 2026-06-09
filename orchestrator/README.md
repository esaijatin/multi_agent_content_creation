# AstraOS Orchestrator (LangGraph)

Central **workflow control plane** with Redis checkpointing and Ollama-backed agents.

## Phase 2 capabilities

- Async workflow execution (non-blocking start)
- Redis LangGraph checkpoints (survive restarts)
- `ModelService` → Ollama (no direct agent calls to Ollama)
- Real **Planner** and **Draft Writer** agents with Pydantic schemas
- Structured execution events in Redis + API sync to PostgreSQL

## Architecture

```
API Gateway ──HTTP──▶ ExecutionService ──▶ LangGraph (Redis checkpoints)
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              ModelService  StateManager  Agents
                    │
                    ▼
                 Ollama
```

## Internal API

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health (Redis + Ollama) |
| `GET /ready` | Readiness (Redis ping) |
| `POST /internal/workflow/start` | Queue async execution |
| `GET /internal/workflow/{thread_id}/state` | Checkpoint + metadata |
| `GET /internal/workflow/{thread_id}/events` | Execution event log |
| `POST /internal/workflow/{thread_id}/approve` | Human approval |
| `POST /internal/workflow/{thread_id}/revise` | Revision trigger |

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://redis:6379/0` | Checkpoints + metadata |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API |
| `OLLAMA_MODEL_PLANNER` | `qwen2.5:7b` | Planner model |
| `OLLAMA_MODEL_WRITER` | `llama3:8b` | Writer model |
| `OLLAMA_REQUEST_TIMEOUT` | `120` | Seconds |

Pull models after first `docker compose up`:

```bash
./scripts/pull-ollama-models.sh
```

## Local run

```bash
cd orchestrator
pip install -r requirements.txt
# Requires Redis + Ollama reachable
uvicorn app.main:app --reload --port 8001
```

See [../docs/phases/phase-2-core-workflow.md](../docs/phases/phase-2-core-workflow.md).
