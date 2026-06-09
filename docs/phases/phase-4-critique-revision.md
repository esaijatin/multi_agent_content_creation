# Phase 4 — Critique & Revision

**Status: Planned**

## Goals

Implement the full **Critique Panel** and orchestrator-controlled **revision loop** with scoring thresholds.

## Critique agents

| Agent | Checks |
|-------|--------|
| Fact Checker | Hallucinations, unsupported claims, contradictions |
| Engagement Critic | Hook, pacing, retention risks |
| Style Critic | Readability, tone, voice consistency |
| Platform Optimizer | CTA, title, thumbnail opportunities |

## Revision loop

```
Draft → Critique Panel → Aggregate Feedback → Rewrite → Re-score → (repeat)
```

Orchestrator controls:

- `max_revision_iterations`
- `critique_score_threshold`
- Approval logic

## Deliverables

- [ ] Structured critique schemas per agent
- [ ] Feedback aggregation node
- [ ] Revision writer (separate from initial draft writer)
- [ ] Frontend script review panel with approve/revise actions
- [ ] Score dashboard in workflow UI

## Acceptance criteria

1. Workflow iterates until threshold or max iterations
2. Human approval gate blocks premature completion
3. All critique outputs schema-validated before state merge

## Previous / Next

← [Phase 3](phase-3-research-retrieval.md) · → [Phase 5](phase-5-security.md)
