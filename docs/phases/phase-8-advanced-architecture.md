# Phase 8 — Advanced Architecture

**Status: Planned**

## Goals

Event-driven execution, message queues, and Kubernetes readiness.

## Deliverables

- [ ] RabbitMQ integration for async agent tasks
- [ ] Event bus schema: `workflow.started`, `agent.completed`, `workflow.failed`
- [ ] Retry queues with dead-letter handling
- [ ] Helm charts or K8s manifests (Deployments, Services, ConfigMaps, Secrets)
- [ ] Horizontal scaling for stateless API and agent workers
- [ ] Evaluate Temporal vs LangGraph for long-running workflows
- [ ] WebSocket real-time workflow updates on frontend

## Event-driven flow

```
API → publish workflow.started → RabbitMQ
         ↓
Orchestrator consumer → execute stage → publish agent.completed
         ↓
Optional agent workers (decoupled containers)
```

## Kubernetes readiness checklist

- [ ] Health/readiness probes on all services
- [ ] Config via env + Secrets (no baked credentials)
- [ ] Stateless services behind load balancers
- [ ] PersistentVolumeClaims for Postgres, Redis, Chroma, MinIO
- [ ] NetworkPolicies for agent isolation

## Acceptance criteria

1. Workflow start succeeds with API and orchestrator on separate nodes
2. Failed agent message retries without corrupting checkpoint state
3. `docker compose` parity documented for local → K8s migration

## Previous

← [Phase 7](phase-7-local-ai.md)
