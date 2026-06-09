# AstraOS API Gateway

FastAPI service acting as the **API Gateway** for AstraOS: authentication, project management, workflow lifecycle APIs, audit logging, and orchestrator delegation.

## Responsibilities

| Layer | Responsibility |
|-------|----------------|
| API Gateway | REST endpoints, request validation, CORS |
| Auth | JWT issuance, RBAC hooks (expanded Phase 5) |
| Persistence | PostgreSQL via SQLAlchemy async |
| Orchestration client | Delegates execution to LangGraph service |

## Quick start (local)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit DATABASE_URL for localhost if not using Docker
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

## Quick start (Docker)

From repository root:

```bash
docker compose up api --build
```

## API endpoints (Phase 1)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | Obtain JWT |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/workflow/start` | Start content workflow |
| GET | `/api/v1/workflow/{id}` | Workflow metadata |
| GET | `/api/v1/workflow/{id}/state` | Workflow state snapshot |
| GET | `/api/v1/workflow/{id}/logs` | Audit / activity logs |
| POST | `/api/v1/workflow/{id}/approve` | Human approval gate |
| POST | `/api/v1/workflow/{id}/revise` | Trigger revision loop |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

## Default dev credentials

After seeding:

- Email: `admin@astraos.local`
- Password: `astraos_dev_2024`

## Project structure

```
app/
├── api/v1/          # REST routers
├── core/            # Config, security, dependencies
├── db/              # Session, seed
├── models/          # SQLAlchemy + Pydantic schemas
├── services/        # Business logic, orchestrator client
└── main.py          # Application factory
```

## Environment

See root `.env.example`. Required:

- `JWT_SECRET_KEY` (min 32 chars)
- `DATABASE_URL`
- `ORCHESTRATOR_URL`

## Phase roadmap

- **Phase 2**: Planner + writer agents wired through orchestrator
- **Phase 3**: RAG + research agent
- **Phase 4**: Critique panel + revision scoring
- **Phase 5**: Full RBAC + service auth
- **Phase 6**: OpenTelemetry instrumentation

See [../docs/phases/README.md](../docs/phases/README.md).
