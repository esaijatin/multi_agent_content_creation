# Phase 5 — Security Hardening

**Status: Planned**

## Goals

Enterprise-grade security: full RBAC, service authentication, validation, and audit.

## Deliverables

- [ ] RBAC policy engine (roles: admin, operator, viewer, service)
- [ ] Per-agent permission enforcement middleware
- [ ] Service-to-service JWT or mTLS between API ↔ orchestrator ↔ agents
- [ ] Input sanitization expansion (prompt injection, oversized payloads)
- [ ] Output moderation + hallucination risk scoring before downstream handoff
- [ ] Immutable audit log retention policy
- [ ] Rate limiting and request size caps at gateway

## Agent permission matrix (enforceable)

| Agent | Internet | Secrets | Retrieval | Workflow write |
|-------|----------|---------|-----------|----------------|
| Research | ✓ | ✗ | ✓ | orchestrator only |
| Writer | ✗ | ✗ | ✓ | orchestrator only |
| Critique | ✗ | ✗ | read-only | ✗ |

## Acceptance criteria

1. Unauthorized role cannot start workflows or approve
2. Agent container/network policy denies out-of-scope access
3. Security events appear in audit log with actor attribution

## Previous / Next

← [Phase 4](phase-4-critique-revision.md) · → [Phase 6](phase-6-observability.md)
