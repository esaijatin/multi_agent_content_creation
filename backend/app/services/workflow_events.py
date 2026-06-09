import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import WorkflowEvent


async def persist_orchestrator_events(
    db: AsyncSession,
    workflow_id: uuid.UUID,
    events: list[dict[str, Any]],
) -> int:
    """Sync orchestrator events into PostgreSQL (idempotent by timestamp+stage)."""
    if not events:
        return 0

    existing = await db.execute(
        select(WorkflowEvent.stage, WorkflowEvent.message, WorkflowEvent.agent).where(
            WorkflowEvent.workflow_id == workflow_id
        )
    )
    seen = {(row.stage, row.message, row.agent) for row in existing.all()}

    inserted = 0
    for ev in events:
        stage = ev.get("stage", "unknown")
        message = ev.get("message", "")
        agent = ev.get("agent")
        key = (stage, message, agent)
        if key in seen:
            continue
        db.add(
            WorkflowEvent(
                workflow_id=workflow_id,
                stage=stage,
                agent=ev.get("agent"),
                message=ev.get("message", ""),
                duration_ms=ev.get("duration_ms"),
                token_usage=ev.get("token_usage", {}),
                error=ev.get("error"),
                metadata_=ev.get("metadata", {}),
            )
        )
        inserted += 1
    if inserted:
        await db.flush()
    return inserted
