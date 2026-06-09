# AstraOS Frontend

Enterprise orchestration dashboard built with **Next.js 15**, **TypeScript**, **Tailwind CSS**, and **shadcn/ui**-style components.

## Design philosophy

This is **not** a chatbot UI. It mirrors internal platforms for workflow orchestration, observability, and agent monitoring.

## Sections

| Route | Purpose |
|-------|---------|
| `/` | JWT authentication |
| `/dashboard` | Project management |
| `/dashboard/workflows` | Pipeline visualization + execution |
| `/dashboard/prompts` | Agent prompt workspace (Phase 2) |
| `/dashboard/review` | Script review & approval (Phase 4) |
| `/dashboard/observability` | Metrics & tracing (Phase 6) |
| `/dashboard/agents` | Agent permission matrix |

## Development

```bash
cd frontend
npm install
cp ../.env.example ../.env
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Docker

Built as part of root `docker compose up`.

## Environment

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | API Gateway base URL |

## Stack

- Next.js App Router
- Radix UI primitives
- Tailwind + CSS variables (dark enterprise theme)
- Lucide icons

See [../docs/phases/phase-1-foundation.md](../docs/phases/phase-1-foundation.md).
