# Phase 2 — Core Workflow

**Status: Complete (v0.2)**

## Goals

Real orchestration persistence, Redis checkpointing, Ollama LLM integration, and production-style async workflow execution with real Planner and Writer agents.

## Deliverables

### Model infrastructure

- [x] `ModelService` abstraction (`orchestrator/app/services/model_service.py`)
- [x] `OllamaProvider` — isolated HTTP client
- [x] Config-driven model routing (`OLLAMA_MODEL_PLANNER`, `OLLAMA_MODEL_WRITER`)
- [x] `structured_generate()` with schema validation and retries
- [x] Ollama in default Docker Compose stack

### Persistence & checkpointing

- [x] Redis-backed LangGraph `AsyncRedisSaver`
- [x] `StateManager` — execution metadata + event history in Redis
- [x] Workflow recovery on orchestrator restart (`recover_interrupted`)
- [x] PostgreSQL `workflow_events` table for durable execution logs

### Agents

- [x] **Planner** — LLM → `PlannerOutput` Pydantic schema
- [x] **Draft Writer** — LLM → `WriterOutput` with markdown script
- [x] Remaining stages remain deterministic stubs (Phase 3–4)

### Async execution

- [x] `POST /internal/workflow/start` returns immediately (queued)
- [x] Background `asyncio` task runs LangGraph pipeline
- [x] API returns workflow ID without blocking on LLM calls
- [x] Frontend polls state every 2s

### Backend improvements

- [x] Workflow ownership checks on all workflow endpoints
- [x] Request size limit middleware (1 MB)
- [x] Stricter prompt sanitization
- [x] Extended workflow status enum (`queued`, `awaiting_revision`)
- [x] Token usage and error fields on workflows

### Frontend

- [x] Execution progress panel with live status
- [x] Execution log timeline (duration, tokens, errors)
- [x] Planner output + draft preview

## Orchestrator structure (Phase 2)

```
orchestrator/app/
├── agents/          # planner, writer, stubs, base
├── api/             # FastAPI routes
├── checkpoints/     # Redis checkpointer lifecycle
├── logging/         # structured orchestration events
├── schemas/         # Pydantic agent I/O
├── services/        # model, execution, state
├── state/           # WorkflowState typed dict
├── utils/           # exceptions, JSON parsing
└── workflows/       # LangGraph graph definition
```

## Run Phase 2

```bash
cp .env.example .env
docker compose up --build -d
chmod +x scripts/pull-ollama-models.sh
./scripts/pull-ollama-models.sh
```

Open http://localhost:3000 → create project → start workflow.

## Acceptance criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | User submits workflow | ✅ |
| 2 | Async execution (immediate ID) | ✅ |
| 3 | Planner via Ollama + structured JSON | ✅ |
| 4 | Writer produces markdown script | ✅ |
| 5 | State in Redis checkpoints | ✅ |
| 6 | Survives orchestrator restart | ✅ |
| 7 | Execution history in logs | ✅ |
| 8 | Frontend shows live progress | ✅ |
| 9 | Schema validation | ✅ |
| 10 | Docker Compose stack | ✅ |

## Known limitations (Phase 3+)

- Research/critique agents still stubs
- No RabbitMQ event bus yet
- No streaming responses to UI
- Full RBAC deferred to Phase 5

## Previous / Next

← [Phase 1](phase-1-foundation.md) · → [Phase 3](phase-3-research-retrieval.md)
