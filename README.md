# AstraOS

**Enterprise-grade multi-agent AI content orchestration platform.**

AstraOS is a production-style autonomous workflow engine for secure, observable, modular AI agent systems. It demonstrates how organizations build internal AI platforms — not a chatbot wrapper.

```
Frontend (Next.js)
        ↓
API Gateway (FastAPI)
        ↓
Auth & RBAC
        ↓
Orchestrator (LangGraph)
        ↓
Agent Runtime (isolated nodes)
        ↓
PostgreSQL · Redis · (Chroma · MinIO · Ollama)
```

## What this project teaches

- Deterministic workflow orchestration (LangGraph)
- Agent isolation and permission scoping
- Distributed service boundaries
- State persistence and auditability
- Enterprise security patterns (JWT, RBAC hooks)
- Infrastructure realism (Docker Compose → K8s-ready)

## Quick start

**New to the project?** Follow the full walkthrough: **[docs/BEGINNER_SETUP_GUIDE.md](docs/BEGINNER_SETUP_GUIDE.md)**

```bash
# 1. Configure environment
cp .env.example .env

# 2. Start the stack
docker compose up --build -d

# 3. Pull Ollama models (first run only)
./scripts/pull-ollama-models.sh

# Seed runs automatically on API startup (see backend/app/db/seed.py)
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| Orchestrator health | http://localhost:8001/health |

**Default login:** `admin@astraos.local` / `astraos_dev_2024`

## Repository structure

```
├── backend/          # FastAPI API Gateway
├── orchestrator/     # LangGraph workflow engine
├── frontend/         # Next.js enterprise dashboard
├── infrastructure/   # Postgres init, future observability configs
└── docs/             # Documentation
    ├── BEGINNER_SETUP_GUIDE.md  # Step-by-step for beginners
    ├── PROJECT_SUMMARY.md   # What has been done so far
    ├── COMMANDS.md          # Command reference
    └── phases/              # Phase-by-phase READMEs
```

## Development phases

| Phase | Focus | README |
|-------|--------|--------|
| 1 | Foundation | [phase-1-foundation.md](docs/phases/phase-1-foundation.md) |
| 2 | Core workflow (current) | [phase-2-core-workflow.md](docs/phases/phase-2-core-workflow.md) |
| 3 | RAG + research agent | [phase-3-research-retrieval.md](docs/phases/phase-3-research-retrieval.md) |
| 4 | Critique + revision loop | [phase-4-critique-revision.md](docs/phases/phase-4-critique-revision.md) |
| 5 | Security hardening | [phase-5-security.md](docs/phases/phase-5-security.md) |
| 6 | Observability | [phase-6-observability.md](docs/phases/phase-6-observability.md) |
| 7 | Local AI (Ollama) | [phase-7-local-ai.md](docs/phases/phase-7-local-ai.md) |
| 8 | Event-driven (RabbitMQ) | [phase-8-advanced-architecture.md](docs/phases/phase-8-advanced-architecture.md) |

## Workflow pipeline

```
Planner → Research → Knowledge → Narrative → Writer → Critique Panel → Revision* → Approval
```

All execution flows through the orchestrator. Agents do not communicate peer-to-peer.

## API overview

```
POST /api/v1/auth/login
POST /api/v1/projects
POST /api/v1/workflow/start
GET  /api/v1/workflow/{id}
GET  /api/v1/workflow/{id}/state
GET  /api/v1/workflow/{id}/logs
POST /api/v1/workflow/{id}/approve
POST /api/v1/workflow/{id}/revise
```

## Full infrastructure profile

```bash
docker compose --profile full up --build
```

Includes Chroma, MinIO, and Ollama for later phases.

## Engineering principles

- Deterministic workflows over autonomous loops
- Structured schemas for all agent I/O
- No hardcoded secrets (use `.env` / Docker secrets)
- Every service: health endpoint, containerized, replaceable
- Observability and audit logs from day one

## License

MIT (add license file as needed for your organization).
