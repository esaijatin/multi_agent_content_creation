# AstraOS — Complete Beginner Setup Guide

This guide assumes you are **new to the project** and want to run AstraOS on your machine from zero. Every command is listed **in the order you should run it**, with a plain-English explanation of **what it does** and **why you need it**.

If you only want a quick command cheat sheet, see [COMMANDS.md](COMMANDS.md).  
If you want to know what has been built so far, see [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md).

---

## Table of contents

1. [What is AstraOS? (in simple terms)](#1-what-is-astraos-in-simple-terms)
2. [What you are about to run](#2-what-you-are-about-to-run)
3. [Prerequisites — install these first](#3-prerequisites--install-these-first)
4. [Step-by-step setup (Docker — recommended)](#4-step-by-step-setup-docker--recommended)
5. [Using the web dashboard](#5-using-the-web-dashboard)
6. [Verify everything works (health checks)](#6-verify-everything-works-health-checks)
7. [Run a workflow end-to-end (API with curl)](#7-run-a-workflow-end-to-end-api-with-curl)
8. [Useful day-to-day commands](#8-useful-day-to-day-commands)
9. [Stopping, restarting, and resetting](#9-stopping-restarting-and-resetting)
10. [Troubleshooting common problems](#10-troubleshooting-common-problems)
11. [Optional: run without Docker (advanced)](#11-optional-run-without-docker-advanced)
12. [Glossary](#12-glossary)
13. [Quick copy-paste checklist](#13-quick-copy-paste-checklist)

---

## 1. What is AstraOS? (in simple terms)

AstraOS is **not a simple ChatGPT wrapper**. It is a **multi-service platform** that:

1. Takes your content request (e.g. “write a YouTube script about AI security”).
2. Runs it through a **fixed pipeline of AI agents** (Planner → Research → Writer → Critique → Approval).
3. Stores **workflow state** in databases so work can survive restarts.
4. Shows progress in an **enterprise-style dashboard** (not a chat UI).

Think of it like a **factory assembly line for AI content**, controlled by an **orchestrator**, rather than one big chatbot.

---

## 2. What you are about to run

When you follow this guide, Docker will start **7 containers** that talk to each other:

| Container name | What it is | Port on your machine |
|----------------|------------|----------------------|
| `astraos-frontend` | Web dashboard (Next.js) | **3000** |
| `astraos-api` | REST API / login / projects (FastAPI) | **8000** |
| `astraos-orchestrator` | Workflow engine (LangGraph) | **8001** |
| `astraos-postgres` | Main database (users, projects, workflows) | **5432** |
| `astraos-redis` | Fast cache + workflow checkpoints | **6379** |
| `astraos-ollama` | Local AI models (runs LLMs on your machine) | **11434** |

**You open in your browser:** http://localhost:3000  
**Default login:** `admin@astraos.local` / `astraos_dev_2024`

---

## 3. Prerequisites — install these first

### 3.1 Docker Desktop (required for the easy path)

**What it is:** Docker runs each part of AstraOS in an isolated “container” so you do not have to install Python, Node, Postgres, Redis, and Ollama manually on your Mac.

**Why you need it:** The project is designed to start with one command: `docker compose up`.

**Install:**

- macOS / Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- After install, **open Docker Desktop** and wait until it says Docker is running.

**Verify Docker works:**

```bash
docker --version
```

**Expected output (example):** `Docker version 27.x.x, build ...`

**Why this command:** Confirms the `docker` CLI is installed and on your PATH.

---

```bash
docker compose version
```

**Expected output (example):** `Docker Compose version v2.x.x`

**Why this command:** AstraOS uses `docker compose` (v2), not the old `docker-compose` hyphenated tool.

---

```bash
docker info
```

**Expected output:** Lots of text; no error like `Cannot connect to the Docker daemon`.

**Why this command:** If Docker Desktop is not running, every later command will fail. Fix that **before** continuing.

---

### 3.2 Git (optional but recommended)

**What it is:** Version control. You may already have the project folder without using git.

**Why you need it:** To clone the repo on another machine or pull updates.

**Verify:**

```bash
git --version
```

---

### 3.3 curl (usually pre-installed on macOS)

**What it is:** A command-line tool to hit HTTP URLs (health checks, API tests).

**Verify:**

```bash
curl --version
```

---

### 3.4 Disk space and RAM (important for Ollama)

**Why it matters:** Ollama downloads **large AI model files** (several GB total).

| Resource | Minimum suggestion |
|----------|-------------------|
| Free disk | **15–20 GB** (models + Docker images) |
| RAM | **8 GB** minimum; **16 GB** recommended |

The first workflow run can be **slow** while models load into memory. That is normal.

---

## 4. Step-by-step setup (Docker — recommended)

All commands below assume your **project root** is:

```text
multi_agent_content_creation/
```

If you are not sure where you are:

```bash
pwd
```

**Why:** `pwd` (“print working directory”) shows your current folder. You should be inside the repo root (where `docker-compose.yml` lives).

---

### Step 1 — Go to the project folder

```bash
cd /path/to/multi_agent_content_creation
```

Replace `/path/to/` with your actual path, for example:

```bash
cd ~/multi_agent_content_creation
```

**Why:** Docker Compose reads `docker-compose.yml` from the current directory. Running commands from the wrong folder causes “file not found” errors.

---

### Step 2 — Confirm the compose file exists

```bash
ls -la docker-compose.yml .env.example
```

**Expected:** Both files are listed.

**Why:** Confirms you are in the repository root before copying config or starting containers.

---

### Step 3 — Create your local environment file

```bash
cp .env.example .env
```

**What it does:** Copies the template environment file to `.env`.

**Why you need it:**

- Docker Compose loads variables from `.env` (passwords, URLs, model names).
- `.env` is **gitignored** so you never commit secrets.
- `.env.example` is the safe template committed to the repo.

**You usually do not need to edit `.env` for first run** — defaults work for local development.

---

### Step 4 — (Optional) Inspect your environment file

```bash
cat .env
```

**Why:** Lets you see database passwords, Ollama model names, and API URLs. Useful when debugging connection issues.

**Important variables:**

| Variable | Meaning |
|----------|---------|
| `JWT_SECRET_KEY` | Signs login tokens (change in production) |
| `DATABASE_URL` | How the API connects to Postgres |
| `REDIS_URL` | How services connect to Redis |
| `OLLAMA_MODEL_PLANNER` | Model for the Planner agent (default: `qwen2.5:7b`) |
| `OLLAMA_MODEL_WRITER` | Model for the Writer agent (default: `llama3:8b`) |
| `NEXT_PUBLIC_API_URL` | Where the browser finds the API (`http://localhost:8000`) |

---

### Step 5 — Start Docker Desktop

**Action:** Open the Docker Desktop application. Wait until the whale icon shows **Running**.

**Why:** `docker compose up` cannot work if the Docker daemon is stopped. This is the #1 beginner failure mode.

---

### Step 6 — Build and start all services (first time)

**Option A — Foreground (see logs live, good for first run):**

```bash
docker compose up --build
```

**Option B — Background (recommended after you know it works):**

```bash
docker compose up --build -d
```

**What each flag means:**

| Part | Meaning |
|------|---------|
| `docker compose up` | Start all services defined in `docker-compose.yml` |
| `--build` | Rebuild images from Dockerfiles (needed first time or after code changes) |
| `-d` | “Detached” — run in background so your terminal is free |

**Why `--build` on first run:** The project does not use pre-published images from Docker Hub. Docker **builds** the API, orchestrator, and frontend from source on your machine.

**What happens during this step (may take 5–15 minutes first time):**

1. Downloads base images (Postgres, Redis, Ollama, Node, Python).
2. Runs `pip install` inside backend/orchestrator images.
3. Runs `npm install` and `npm run build` for the frontend.
4. Starts containers in dependency order (Postgres/Redis → Ollama → Orchestrator → API → Frontend).
5. API container runs database seed (creates default admin user).

**When ready, you should see** (foreground mode) lines like:

- `astraos-api` — application startup complete
- `astraos-orchestrator` — orchestrator_starting / recovery complete
- `astraos-frontend` — ready on port 3000

If you used `-d`, check status instead:

```bash
docker compose ps
```

**Expected:** Services show `running` or `healthy` (health checks may take 30–60 seconds).

**Why this command:** Shows which containers are up and whether health checks passed.

---

### Step 7 — Watch logs if something looks wrong (optional)

```bash
docker compose logs -f
```

**Why:** Streams combined logs from all services. Press `Ctrl+C` to stop watching (containers keep running).

**Single service:**

```bash
docker compose logs -f orchestrator
```

**Why:** Planner/Writer errors and Ollama connection issues usually appear in the orchestrator log.

---

### Step 8 — Pull Ollama AI models (required once)

The Ollama container starts **empty**. Models must be downloaded before Planner/Writer agents can run.

**Make the script executable:**

```bash
chmod +x scripts/pull-ollama-models.sh
```

**Why `chmod +x`:** Marks the file as executable so you can run `./scripts/pull-ollama-models.sh` directly.

**Run the script:**

```bash
./scripts/pull-ollama-models.sh
```

**What it does:** Runs `ollama pull` inside the `astraos-ollama` container for:

- `qwen2.5:7b` (Planner)
- `llama3:8b` (Writer)

**Why you need this:** Without models, workflows queue but fail when the orchestrator calls Ollama.

**This step can take a long time** (minutes to tens of minutes depending on internet speed). You will see download progress in the terminal.

**Alternative — run pulls manually:**

```bash
docker exec astraos-ollama ollama pull qwen2.5:7b
docker exec astraos-ollama ollama pull llama3:8b
```

**Why `docker exec`:** Runs a command **inside** a running container. Your Mac does not need Ollama installed natively.

**Verify models are present:**

```bash
docker exec astraos-ollama ollama list
```

**Expected:** Lists `qwen2.5:7b` and `llama3:8b` (or whatever you configured in `.env`).

---

### Step 9 — Confirm services are healthy

Run these **one at a time**:

```bash
curl -s http://localhost:8000/health
```

**Why:** Checks the API Gateway is responding.

**Expected (example):** `{"status":"healthy","service":"api-gateway"}`

---

```bash
curl -s http://localhost:8001/health
```

**Why:** Checks orchestrator + Redis + Ollama connectivity.

**Expected:** JSON with `"service":"orchestrator"`. Ollama may show `"ollama":true` when models are ready.

---

```bash
curl -s http://localhost:8001/ready
```

**Why:** Readiness probe — orchestrator returns 200 only when Redis is reachable (used by Docker healthcheck).

---

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000
```

**Why:** Checks the frontend HTTP server. Expected code: `200` or `307`.

---

### Step 10 — Open the dashboard

**Action:** In your browser, go to:

```text
http://localhost:3000
```

**Why port 3000:** The frontend container maps host port 3000 → container port 3000.

You should see the **AstraOS login page**.

---

## 5. Using the web dashboard

### Step 11 — Log in

| Field | Value |
|-------|--------|
| Email | `admin@astraos.local` |
| Password | `astraos_dev_2024` |

**Why these credentials:** Created automatically when the API starts (`backend/app/db/seed.py`). Dev-only — never use in production.

**If login fails:**

- Confirm API is up: `curl http://localhost:8000/health`
- Check API logs: `docker compose logs api`
- Confirm `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env`

---

### Step 12 — Create a project

1. After login you land on **Project Dashboard**.
2. Enter a name (e.g. `My First Project`).
3. Click **Create**.

**Why a project exists:** Every workflow must belong to a project (organization pattern — projects group workflows).

---

### Step 13 — Start a workflow

1. Click **Start Workflow** on your project (or go to **Workflows** in the sidebar).
2. The URL should include `?project=<uuid>` — the project ID.
3. Edit the prompt textarea if you want.
4. Click **Execute Workflow**.

**What happens behind the scenes:**

1. Browser sends `POST /api/v1/workflow/start` to the API.
2. API creates a workflow row in Postgres (status: `queued`).
3. API tells the orchestrator to start async execution.
4. Orchestrator runs: **Planner (Ollama)** → stub agents → **Writer (Ollama)** → critique → approval.
5. State is saved in **Redis checkpoints**.
6. Frontend polls `/workflow/{id}/state` and `/logs` every 2 seconds.

**First workflow may take several minutes** — Ollama inference is CPU/GPU bound.

**What you should see in the UI:**

- Status badge: `queued` → `running` → possibly `awaiting_approval`
- Pipeline stages lighting up (Planner, Research, Writer, …)
- **Planner Output** JSON panel
- **Generated Draft** markdown panel
- **Execution Log** with timing and token counts

---

### Step 14 — Explore other dashboard pages

| Sidebar item | Purpose |
|--------------|---------|
| Projects | Create/list projects |
| Workflows | Run and monitor pipelines |
| Prompt Workspace | Placeholder (future prompt registry) |
| Script Review | Placeholder (human approval UI — Phase 4) |
| Observability | Placeholder (metrics — Phase 6) |
| Agent Activity | Shows agent permission matrix |

---

## 6. Verify everything works (health checks)

Copy this block after the stack is running:

```bash
echo "=== API ==="
curl -s http://localhost:8000/health | python3 -m json.tool

echo "=== Orchestrator ==="
curl -s http://localhost:8001/health | python3 -m json.tool

echo "=== Ollama models ==="
docker exec astraos-ollama ollama list

echo "=== Containers ==="
docker compose ps
```

**Why `python3 -m json.tool`:** Pretty-prints JSON so it is easier to read (optional).

---

## 7. Run a workflow end-to-end (API with curl)

Use this if you prefer the terminal or want to verify the API without the UI.

### Step 15 — Log in and save token

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@astraos.local","password":"astraos_dev_2024"}'
```

**Why:** Returns a JWT `access_token` required for all other API calls.

**Save token (macOS/Linux):**

```bash
export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@astraos.local","password":"astraos_dev_2024"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token length: ${#TOKEN}"
```

**Why `export TOKEN`:** Stores the token in your shell session so the next commands can use `$TOKEN`.

---

### Step 16 — Create a project

```bash
curl -s -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"CLI Test Project","description":"Created from curl"}' \
  | python3 -m json.tool
```

**Why:** You need a `project_id` UUID to start a workflow.

**Save project ID:**

```bash
export PROJECT_ID=$(curl -s -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"CLI Test Project 2","description":"demo"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Project ID: $PROJECT_ID"
```

---

### Step 17 — Start a workflow

```bash
curl -s -X POST http://localhost:8000/api/v1/workflow/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": \"$PROJECT_ID\",
    \"content_request\": {
      \"prompt\": \"Write a 5-minute YouTube script about how Redis checkpointing helps AI workflows survive restarts.\",
      \"platform\": \"youtube\",
      \"audience\": \"software engineers\",
      \"tone\": \"professional\",
      \"complexity\": \"medium\"
    }
  }" | python3 -m json.tool
```

**Why:** Returns immediately with workflow `id` and status `queued` — execution continues in the background.

**Save workflow ID:**

```bash
export WORKFLOW_ID=$(curl -s -X POST http://localhost:8000/api/v1/workflow/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": \"$PROJECT_ID\",
    \"content_request\": {
      \"prompt\": \"Write a short YouTube script about multi-agent orchestration.\",
      \"platform\": \"youtube\",
      \"audience\": \"developers\",
      \"tone\": \"professional\",
      \"complexity\": \"low\"
    }
  }" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Workflow ID: $WORKFLOW_ID"
```

---

### Step 18 — Poll workflow state

```bash
curl -s http://localhost:8000/api/v1/workflow/$WORKFLOW_ID/state \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Why:** Shows current stage, status, token usage, and state snapshot (planner output, draft, etc.).

**Run multiple times** until `status` is `awaiting_approval`, `completed`, or `failed`.

---

### Step 19 — View execution logs

```bash
curl -s http://localhost:8000/api/v1/workflow/$WORKFLOW_ID/logs \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Why:** Shows per-agent events (stage, duration_ms, token_usage, errors).

---

### Step 20 — Approve workflow (optional)

When status is `awaiting_approval`:

```bash
curl -s -X POST http://localhost:8000/api/v1/workflow/$WORKFLOW_ID/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "feedback": null}' \
  | python3 -m json.tool
```

**Why:** Human-in-the-loop gate — marks workflow completed in the orchestration pipeline.

---

## 8. Useful day-to-day commands

### See what is running

```bash
docker compose ps
```

---

### Follow logs

```bash
# All services
docker compose logs -f

# Just orchestrator (LLM + workflow errors)
docker compose logs -f orchestrator

# Just API (auth / database errors)
docker compose logs -f api
```

---

### Restart one service after code changes

```bash
docker compose up --build -d orchestrator
```

**Why:** Rebuilds only the orchestrator image and recreates that container.

---

### Open API interactive docs

Browser: **http://localhost:8000/docs**

**Why:** Swagger UI — try endpoints with “Authorize” using your JWT token.

---

### Connect to Postgres (inspect data)

```bash
docker exec -it astraos-postgres psql -U astraos -d astraos
```

**Inside psql:**

```sql
\dt                    -- list tables
SELECT email, role FROM users;
SELECT id, status, current_stage FROM workflows ORDER BY created_at DESC LIMIT 5;
\q                     -- quit
```

**Why:** Useful when debugging whether workflows are persisted correctly.

---

### Connect to Redis (inspect checkpoints keys)

```bash
docker exec -it astraos-redis redis-cli
```

**Inside redis-cli:**

```redis
PING
KEYS astraos:*
```

**Why:** Phase 2 stores workflow metadata and LangGraph checkpoint data in Redis.

---

## 9. Stopping, restarting, and resetting

### Stop containers (keep data)

```bash
docker compose down
```

**Why:** Stops all services but **keeps volumes** (Postgres data, Redis data, Ollama models).

---

### Start again (no rebuild)

```bash
docker compose up -d
```

**Why:** Faster restart when you have not changed code or Dockerfiles.

---

### Stop and delete all data (fresh start)

```bash
docker compose down -v
```

**Why `-v`:** Removes named volumes — **wipes database, Redis, and downloaded Ollama models**. You will need to run `./scripts/pull-ollama-models.sh` again.

**Warning:** This deletes all projects and workflows stored locally.

---

### Full rebuild from scratch

```bash
docker compose down -v
docker compose up --build -d
chmod +x scripts/pull-ollama-models.sh
./scripts/pull-ollama-models.sh
```

---

## 10. Troubleshooting common problems

### “Cannot connect to the Docker daemon”

**Cause:** Docker Desktop is not running.

**Fix:** Open Docker Desktop → wait until running → retry `docker compose up`.

---

### Port already in use (3000, 8000, 8001, 5432, 6379, 11434)

**Cause:** Another app uses the same port.

**Check what uses a port (macOS example):**

```bash
lsof -i :8000
```

**Fix options:**

- Stop the conflicting app, or
- Change ports in `docker-compose.yml` (e.g. `"8001:8001"` → `"8011:8001"`)

---

### Login works in UI but workflows fail immediately

**Check orchestrator:**

```bash
docker compose logs orchestrator --tail 100
```

**Common causes:**

1. Ollama models not pulled → run `./scripts/pull-ollama-models.sh`
2. Ollama still downloading → wait and check `docker exec astraos-ollama ollama list`
3. Model name mismatch → verify `.env` matches pulled models

---

### Workflow stuck on `queued` or `running` forever

**Check:**

```bash
curl -s http://localhost:8001/health | python3 -m json.tool
docker compose logs orchestrator --tail 50
```

**Cause:** LLM inference can be slow on CPU-only machines (5–15+ minutes is possible).

---

### `ollama pull` fails or is very slow

**Cause:** Network or disk space.

**Check disk:**

```bash
df -h
```

**Retry single model:**

```bash
docker exec astraos-ollama ollama pull qwen2.5:7b
```

**Use smaller models (edit `.env` then restart orchestrator):**

```env
OLLAMA_MODEL_PLANNER=qwen2.5:3b
OLLAMA_MODEL_WRITER=qwen2.5:3b
```

```bash
docker compose up -d orchestrator
docker exec astraos-ollama ollama pull qwen2.5:3b
```

---

### Frontend shows “Authentication failed”

**Checks:**

```bash
curl http://localhost:8000/health
docker compose logs api --tail 30
```

**Cause:** API not ready yet, or seed user not created. Wait 30s after `docker compose up` and retry.

---

### Database schema errors after upgrading code

**Nuclear option (dev only):**

```bash
docker compose down -v
docker compose up --build -d
```

**Why:** Phase 2 adds new columns/tables; SQLAlchemy creates them on API startup, but a corrupted volume may need reset.

---

### Orchestrator unhealthy / `/ready` fails

**Cause:** Redis not ready.

```bash
docker compose ps redis
docker compose logs redis
```

**Fix:**

```bash
docker compose restart redis orchestrator
```

---

## 11. Optional: run without Docker (advanced)

Only try this if you are comfortable installing dependencies manually.

**Requirements:**

- Python **3.12** (not 3.14 — Pydantic wheels may fail on 3.14)
- Node.js **20+**
- Postgres and Redis running locally
- Ollama installed natively or reachable at `http://localhost:11434`

**Start infrastructure only with Docker:**

```bash
docker compose up postgres redis ollama -d
./scripts/pull-ollama-models.sh
```

**Backend:**

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Edit ../.env: DATABASE_URL and REDIS_URL point to localhost
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

**Orchestrator (new terminal):**

```bash
cd orchestrator
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# OLLAMA_BASE_URL=http://localhost:11434 in .env
uvicorn app.main:app --reload --port 8001
```

**Frontend (new terminal):**

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

**Why people use Docker instead:** One command, matching versions, no local Python/Node conflicts.

---

## 12. Glossary

| Term | Meaning |
|------|---------|
| **API Gateway** | The FastAPI backend (`astraos-api`) — login, projects, workflows |
| **Orchestrator** | LangGraph service that runs the agent pipeline in order |
| **Agent** | One step in the pipeline (Planner, Writer, etc.) |
| **Workflow** | One end-to-end run from user prompt to draft/approval |
| **Checkpoint** | Saved graph state in Redis so work survives restarts |
| **Ollama** | Runs open-source LLMs locally on your machine |
| **JWT** | Token returned at login; sent as `Authorization: Bearer ...` |
| **Docker Compose** | Tool to start multiple containers from `docker-compose.yml` |
| **Volume** | Persistent disk storage for container data (DB, models) |
| **Thread ID** | Orchestrator internal ID (`thread-<workflow-uuid>`) |

---

## 13. Quick copy-paste checklist

Run these **in order** from the project root:

```bash
# 1. Go to project
cd ~/multi_agent_content_creation

# 2. Environment file
cp .env.example .env

# 3. Verify Docker is running
docker info

# 4. Start everything (first time — takes several minutes)
docker compose up --build -d

# 5. Wait for health (optional loop)
sleep 30
docker compose ps

# 6. Download AI models (first time only — can take a long time)
chmod +x scripts/pull-ollama-models.sh
./scripts/pull-ollama-models.sh

# 7. Verify health
curl -s http://localhost:8000/health
curl -s http://localhost:8001/health
docker exec astraos-ollama ollama list

# 8. Open browser → http://localhost:3000
#    Login: admin@astraos.local / astraos_dev_2024
#    Create project → Workflows → Execute Workflow
```

---

## What to read next

| Document | When to read it |
|----------|-----------------|
| [COMMANDS.md](COMMANDS.md) | You know the basics and want a command reference |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | You want to understand what is implemented |
| [phases/phase-2-core-workflow.md](phases/phase-2-core-workflow.md) | You want Phase 2 technical details |
| [../backend/README.md](../backend/README.md) | You are developing the API |
| [../orchestrator/README.md](../orchestrator/README.md) | You are developing agents/orchestration |

---

## Summary

1. **Install Docker Desktop** and keep it running.  
2. **`cp .env.example .env`** — local configuration.  
3. **`docker compose up --build -d`** — starts the full platform.  
4. **`./scripts/pull-ollama-models.sh`** — downloads AI models (required once).  
5. Open **http://localhost:3000** and log in.  
6. Create a **project**, then **execute a workflow** and watch the pipeline progress.

You are now running a real multi-service AI orchestration stack — not a single-script demo.
