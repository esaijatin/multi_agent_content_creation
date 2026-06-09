# AstraOS — Command Reference

All commands for setting up, running, developing, and verifying the platform. Commands are grouped by purpose.

---

## Initial setup

From the repository root:

```bash
# Copy environment template (never commit .env)
cp .env.example .env

# Optional: edit secrets and connection strings
# open .env   # macOS
# nano .env
```

---

## Ollama models (Phase 2 — required once)

After the stack is running:

```bash
chmod +x scripts/pull-ollama-models.sh
./scripts/pull-ollama-models.sh

# Or manually:
docker exec astraos-ollama ollama pull qwen2.5:7b
docker exec astraos-ollama ollama pull llama3:8b
```

## Docker Compose (recommended)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine) running.

```bash
# Start full Phase 1 stack (API, orchestrator, frontend, Postgres, Redis)
docker compose up --build

# Start in detached (background) mode
docker compose up --build -d

# Stop all services
docker compose down

# Stop and remove volumes (fresh database)
docker compose down -v

# Rebuild specific services only
docker compose build api orchestrator frontend

# View logs (all services)
docker compose logs -f

# View logs for one service
docker compose logs -f api
docker compose logs -f orchestrator
docker compose logs -f frontend
```

### Full infrastructure profile (Phase 3+ services)

Includes Chroma, MinIO, and Ollama:

```bash
docker compose --profile full up --build
```

### Start individual services

```bash
docker compose up postgres redis -d
docker compose up api orchestrator --build
docker compose up frontend --build
```

---

## Health checks

```bash
# API Gateway
curl http://localhost:8000/health

# Orchestrator
curl http://localhost:8001/health

# Prometheus metrics (API)
curl http://localhost:8000/metrics
```

---

## Authentication & API (curl)

Default dev user (created by seed): `admin@astraos.local` / `astraos_dev_2024`

```bash
# Login — save token
export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@astraos.local","password":"astraos_dev_2024"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Current user
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Create project
curl -s -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo Project","description":"Test project"}' | python3 -m json.tool

# List projects
curl -s http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Start workflow (replace PROJECT_ID)
export PROJECT_ID="<your-project-uuid>"
curl -s -X POST http://localhost:8000/api/v1/workflow/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": \"$PROJECT_ID\",
    \"content_request\": {
      \"prompt\": \"Create a YouTube script about secure multi-agent AI systems.\",
      \"platform\": \"youtube\",
      \"audience\": \"engineering leaders\",
      \"tone\": \"professional\",
      \"complexity\": \"high\"
    }
  }" | python3 -m json.tool

# Get workflow state (replace WORKFLOW_ID)
export WORKFLOW_ID="<your-workflow-uuid>"
curl -s http://localhost:8000/api/v1/workflow/$WORKFLOW_ID/state \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Workflow audit logs
curl -s http://localhost:8000/api/v1/workflow/$WORKFLOW_ID/logs \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Approve workflow
curl -s -X POST http://localhost:8000/api/v1/workflow/$WORKFLOW_ID/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "feedback": null}' | python3 -m json.tool

# Request revision
curl -s -X POST http://localhost:8000/api/v1/workflow/$WORKFLOW_ID/revise \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feedback": "Strengthen the opening hook.", "target_stage": null}' | python3 -m json.tool
```

### Orchestrator internal API (service-to-service)

Uses `X-Internal-Api-Key` from `.env` (`ORCHESTRATOR_INTERNAL_API_KEY`).

```bash
export INTERNAL_KEY="orchestrator-internal-dev-key"

curl -s -X POST http://localhost:8001/internal/workflow/start \
  -H "X-Internal-Api-Key: $INTERNAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"workflow_id":"test-123","payload":{"platform":"youtube","audience":"devs","complexity":"medium","prompt":"test"}}' \
  | python3 -m json.tool
```

---

## Local development (without Docker)

Use **Python 3.12** (Docker images use 3.12). Python 3.14 may fail to install `pydantic-core` wheels locally.

### PostgreSQL & Redis

Run via Docker or install locally, then set `DATABASE_URL` and `REDIS_URL` in `.env` to point at `localhost`.

```bash
docker compose up postgres redis -d
```

### Backend (API Gateway)

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# From repo root — ensure .env exists
export $(grep -v '^#' ../.env | xargs)   # optional: load env vars

python -m app.db.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Orchestrator (LangGraph)

```bash
cd orchestrator
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Verify graph compiles:

```bash
python -c "from app.graph.workflow import compile_workflow; g=compile_workflow(); print('OK')"
```

### Frontend (Next.js)

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Production build:

```bash
npm run build
npm run start
```

---

## Database

```bash
# Connect to Postgres inside Docker
docker exec -it astraos-postgres psql -U astraos -d astraos

# Common psql commands
# \dt          — list tables
# \d users     — describe table
# SELECT * FROM users;
```

```bash
# Redis CLI inside Docker
docker exec -it astraos-redis redis-cli
# PING
# KEYS *
```

---

## Git (optional)

```bash
git init
git add .
git status
git commit -m "Initial AstraOS Phase 1 foundation"
```

---

## Commands run during initial project scaffolding

These were used while building the repository (for reference):

```bash
# Inspect empty workspace
ls -la /Users/jatineppili/multi_agent_content_creation

# Create local env file from template
cp .env.example .env

# Attempt local Python venv + dependency install (orchestrator)
cd orchestrator
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -c "from app.graph.workflow import compile_workflow; g=compile_workflow(); print('graph ok', g)"

# Attempt local Python venv + dependency install (backend)
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -c "from app.main import app; print('api ok', app.title)"

# Attempt Docker image build (requires Docker daemon running)
cd /Users/jatineppili/multi_agent_content_creation
docker compose build api orchestrator
```

**Note:** Local `pip install` failed on the build machine when using system Python 3.14 (pydantic-core / PyO3 compatibility). Docker builds use Python 3.12 and should succeed once Docker Desktop is running.

---

## Service URLs (default ports)

| Service       | URL |
|---------------|-----|
| Frontend      | http://localhost:3000 |
| API           | http://localhost:8000 |
| API docs      | http://localhost:8000/docs |
| Orchestrator  | http://localhost:8001 |
| PostgreSQL    | localhost:5432 |
| Redis         | localhost:6379 |
| Chroma (full) | http://localhost:8100 |
| MinIO (full)  | http://localhost:9000 (API), :9001 (console) |
| Ollama (full) | http://localhost:11434 |

---

## Related docs

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) — what has been built so far
- [phases/phase-1-foundation.md](phases/phase-1-foundation.md) — Phase 1 details
- [../README.md](../README.md) — project overview
