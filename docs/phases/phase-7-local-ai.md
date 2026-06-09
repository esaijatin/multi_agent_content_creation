# Phase 7 — Local AI Infrastructure

**Status: Planned**

## Goals

Minimize external API dependence via **Ollama** and a portable model abstraction layer.

## Deliverables

- [ ] `ModelProvider` interface: `complete`, `stream`, `embed`
- [ ] Ollama adapter with health checks
- [ ] Model routing (per agent, per task complexity)
- [ ] Streaming responses to frontend (WebSocket, Phase 8 UI tie-in)
- [ ] Token usage metrics export
- [ ] Future: vLLM adapter stub for high-throughput deployment

## Configuration

```env
OLLAMA_HOST=http://ollama:11434
OLLAMA_DEFAULT_MODEL=llama3.2
```

## Agent → model routing example

| Agent | Model tier |
|-------|------------|
| Planner | medium |
| Research | medium + embeddings |
| Writer | large |
| Critique | small (fast) |

## Acceptance criteria

1. Full workflow runnable with zero external LLM API keys
2. Model swap requires only config change, not code change
3. Failed model calls trigger orchestrator retry policy

## Previous / Next

← [Phase 6](phase-6-observability.md) · → [Phase 8](phase-8-advanced-architecture.md)
