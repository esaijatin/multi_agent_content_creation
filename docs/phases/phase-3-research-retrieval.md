# Phase 3 — Research & Retrieval

**Status: Planned**

## Goals

Add RAG pipeline, Chroma vector store, and the **Research Agent** with semantic retrieval.

## Deliverables

- [ ] Enable `chroma` + `minio` in default or documented compose profile
- [ ] Ingestion pipeline: chunking, embedding, indexing
- [ ] Research agent: retrieve, summarize, rank sources, extract concepts
- [ ] Knowledge Consolidation agent: dedupe, resolve contradictions
- [ ] Context assembly with retrieval scoring (no full-document prompt dumps)
- [ ] Creator memory / historical workflow knowledge indexing

## RAG pipeline

```
Ingest → Chunk → Embed → Index (Chroma)
                ↓
Query → Retrieve → Score → Assemble context → Agent
```

## Research agent permissions

| Capability | Allowed |
|------------|---------|
| Internet | Yes |
| Secrets | No |
| Write workflow state | Via orchestrator only |

## Acceptance criteria

1. Research agent returns structured `research_summary` with ranked sources
2. Vector search latency tracked (prep for Phase 6 metrics)
3. Oversized retrieval contexts rejected at validation layer

## Previous / Next

← [Phase 2](phase-2-core-workflow.md) · → [Phase 4](phase-4-critique-revision.md)
