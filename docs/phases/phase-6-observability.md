# Phase 6 — Observability

**Status: Planned**

## Goals

Production observability: metrics, tracing, dashboards, centralized logging.

## Stack

| Component | Purpose |
|-----------|---------|
| Prometheus | Metrics scrape (`/metrics` on all services) |
| Grafana | Dashboards: workflow timing, agent latency, queue depth |
| OpenTelemetry | Distributed traces across API → orchestrator → agents |
| Loki or ELK | Structured log aggregation |

## Metrics to track

- Workflow duration per stage
- Agent invocation latency
- Retry counts
- Queue depth (when RabbitMQ live)
- Token usage (when LLM integrated)
- Failure rates by agent

## Deliverables

- [ ] OTEL instrumentation on FastAPI and orchestrator
- [ ] Prometheus scrape configs in `infrastructure/`
- [ ] Grafana dashboard JSON
- [ ] Frontend observability page with live metrics embed
- [ ] Correlation IDs propagated through audit logs

## Acceptance criteria

1. Single workflow trace visible end-to-end in Grafana/Tempo
2. Alerting rules defined for failure rate > threshold
3. Logs queryable by `workflow_id`

## Previous / Next

← [Phase 5](phase-5-security.md) · → [Phase 7](phase-7-local-ai.md)
