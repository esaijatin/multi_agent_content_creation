# AstraOS — Project Summary (Work Completed So Far)

**Last updated:** Phase 1 foundation  
**Status:** Scaffold complete, ready for `docker compose up` and Phase 2 development

---

## Executive summary

AstraOS is an **enterprise-style multi-agent AI content orchestration platform**. The repository was created from an empty workspace and implements **Phase 1 (Foundation Infrastructure)** of an eight-phase roadmap.

The system is designed as a **layered distributed architecture** (dashboard → API gateway → orchestrator → isolated agents → data stores), not a chatbot wrapper. Content creation is the **showcase workflow** for orchestration, security, and observability patterns.

**Phase 1 is complete.** Phases 2–8 are documented but not yet implemented.

---

## Architecture delivered

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Next.js 15, TypeScript, Tailwind, shadcn UI)   │
│  Enterprise dashboard — not a chat UI                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST / JWT
┌───────────────────────────▼─────────────────────────────────┐
│  API Gateway (FastAPI)                                       │
│  Auth · Projects · Workflows · Audit · Metrics               │
└───────────┬─────────────────────────────┬─────────────────────┘
            │                             │
            ▼                             ▼
┌───────────────────┐         ┌───────────────────────────────┐
│  PostgreSQL       │         │  Orchestrator (LangGraph)     │
│  Workflows, audit │         │  Deterministic StateGraph      │
└───────────────────┘         └───────────────┬───────────────┘
            ▲                                 │
┌───────────┴───────────┐                     ▼
│  Redis                │         ┌───────────────────────────┐
│  Cache / future       │         │  Agent nodes (isolated)    │
│  checkpoints          │         │  Planner + stubs           │
└───────────────────────┘         └───────────────────────────┘
```

**Design principles enforced in code:**

- Deterministic workflow graph (no uncontrolled agent loops)
- Agents communicate only via orchestrator state
- Structured request/response schemas (Pydantic)
- JWT authentication and role enum (RBAC hooks for Phase 5)
- Audit logging on key actions
- Secrets via environment variables only
- Every app service exposes `/health`

---

## Repository structure created

| Path | Purpose |
|------|---------|
| `backend/` | FastAPI API Gateway |
| `orchestrator/` | LangGraph workflow engine |
| `frontend/` | Next.js enterprise dashboard |
| `infrastructure/` | Postgres init SQL, infra README |
| `docs/` | Documentation hub |
| `docs/phases/` | README per development phase (1–8) |
| `docker-compose.yml` | Full local stack |
| `.env.example` | Environment template |
| `.gitignore` | Python, Node, secrets exclusions |

---

## Phase 1 — What was implemented

### Infrastructure & DevOps

- [x] Monorepo layout with service boundaries
- [x] `docker-compose.yml` — `api`, `orchestrator`, `frontend`, `postgres`, `redis`
- [x] Optional `--profile full` for Chroma, MinIO, Ollama (future phases)
- [x] Health checks and service dependency ordering
- [x] `.env.example` with all planned configuration keys
- [x] PostgreSQL init script (`infrastructure/postgres/init.sql`)

### API Gateway (`backend/`)

- [x] FastAPI application with CORS and lifespan DB init
- [x] **JWT auth:** `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- [x] **Projects:** create, list, get
- [x] **Workflows:** start, get, state, logs, approve, revise
- [x] SQLAlchemy async models: `User`, `Project`, `Workflow`, `AuditLog`
- [x] Seed script — default admin user on container startup
- [x] Orchestrator HTTP client (internal API key header)
- [x] Audit log service for workflow/project events
- [x] Content request validation + basic prompt-injection patterns
- [x] Prometheus metrics mount at `/metrics`
- [x] Structured logging (structlog)

### Orchestrator (`orchestrator/`)

- [x] LangGraph `StateGraph` with full pipeline:
  - Planner → Research → Knowledge → Narrative → Writer → Critique → Revision → Approval
- [x] **Planner agent** — produces structured `ExecutionPlan` JSON
- [x] **Stub agents** for remaining stages (wired, return placeholder data)
- [x] Conditional routing for revision loop and approval
- [x] Configurable `max_revision_iterations` and `critique_score_threshold`
- [x] Internal REST API (`/internal/workflow/*`) with API key auth
- [x] In-memory thread state (Redis checkpointing planned Phase 2)
- [x] Agent permission definitions stub (`agents/permissions.py`)

### Frontend (`frontend/`)

- [x] Next.js 15 App Router + TypeScript + Tailwind
- [x] shadcn-style UI components (Button, Card, Badge)
- [x] Dark enterprise theme
- [x] **Login page** with JWT stored in `localStorage`
- [x] **Project dashboard** — create/list projects
- [x] **Workflow visualization** — pipeline component + start workflow + live state poll
- [x] Placeholder pages: Prompt Workspace, Script Review, Observability, Agent Activity
- [x] Sidebar navigation matching orchestration platform UX

### Documentation

- [x] Root `README.md`
- [x] `docs/README.md`
- [x] `docs/phases/README.md` + **phase-1 through phase-8** guides
- [x] Per-service READMEs: `backend/`, `orchestrator/`, `frontend/`, `infrastructure/`
- [x] `docs/COMMANDS.md` — command reference
- [x] `docs/PROJECT_SUMMARY.md` — this file

---

## Workflow pipeline (current behavior)

| Stage | Agent | Phase 1 status |
|-------|--------|----------------|
| 1 | Planner | ✅ Structured plan from user request |
| 2 | Research | Stub — returns placeholder summary |
| 3 | Knowledge consolidation | Stub |
| 4 | Narrative strategist | Stub outline |
| 5 | Draft writer | Stub draft text |
| 6 | Critique panel | Stub scores (4 critics) |
| 7 | Revision loop | Logic works; re-critiques until threshold |
| 8 | Approval | Human gate via API |

Orchestrator stops at **awaiting_approval** when critique scores meet threshold or max iterations are reached.

---

## API surface (implemented)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | JWT token |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects` | List projects |
| GET | `/api/v1/projects/{id}` | Get project |
| POST | `/api/v1/workflow/start` | Start orchestrated workflow |
| GET | `/api/v1/workflow/{id}` | Workflow metadata |
| GET | `/api/v1/workflow/{id}/state` | State snapshot |
| GET | `/api/v1/workflow/{id}/logs` | Audit/activity logs |
| POST | `/api/v1/workflow/{id}/approve` | Human approval |
| POST | `/api/v1/workflow/{id}/revise` | Trigger revision |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

---

## Default credentials (development only)

| Field | Value |
|-------|--------|
| Email | `admin@astraos.local` |
| Password | `astraos_dev_2024` |
| Role | `admin` |

Change via seed script or database before any non-local deployment.

---

## What is intentionally NOT done yet

| Area | Planned phase |
|------|----------------|
| Real LLM / Ollama integration | Phase 7 |
| RAG, Chroma, embeddings | Phase 3 |
| Full critique agents with real scoring | Phase 4 |
| Redis-backed LangGraph checkpoints | Phase 2 |
| Alembic migrations | Phase 2 |
| Full RBAC policy engine | Phase 5 |
| Prometheus/Grafana/OpenTelemetry stack | Phase 6 |
| RabbitMQ event bus | Phase 8 |
| WebSocket streaming | Phase 8 |
| Kubernetes manifests | Phase 8 |

---

## How to run (quick reference)

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost:3000 and sign in. See [COMMANDS.md](COMMANDS.md) for the full command list.

---

## Development roadmap (remaining phases)

| Phase | Focus |
|-------|--------|
| **1** | ✅ Foundation — Docker, API, orchestrator, dashboard |
| **2** | Planner + writer with LLM, persistence, Redis checkpoints |
| **3** | Research agent, RAG, Chroma, MinIO |
| **4** | Critique panel, revision scoring, review UI |
| **5** | RBAC, service auth, validation hardening |
| **6** | Metrics, tracing, Grafana, centralized logs |
| **7** | Ollama, model abstraction, routing |
| **8** | RabbitMQ, event-driven execution, K8s readiness |

Details: [docs/phases/README.md](phases/README.md)

---

## Verification status

| Check | Result |
|-------|--------|
| Repository scaffolded | ✅ |
| All Phase 1 source files created | ✅ |
| Documentation (phases + service READMEs) | ✅ |
| Local `pip install` on Python 3.14 | ⚠️ Failed (use 3.12 or Docker) |
| `docker compose build` | ⚠️ Not run — Docker daemon was not available during scaffolding |

**Recommendation:** Start Docker Desktop, then run `docker compose up --build` to verify the full stack.

---

## Related documentation

- [COMMANDS.md](COMMANDS.md) — all commands
- [phases/phase-1-foundation.md](phases/phase-1-foundation.md) — Phase 1 acceptance criteria
- [../README.md](../README.md) — main project README
