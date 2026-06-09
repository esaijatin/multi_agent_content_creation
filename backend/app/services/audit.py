import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AuditLog


async def write_audit_log(
    db: AsyncSession,
    *,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    workflow_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    entry = AuditLog(
        workflow_id=workflow_id,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
    )
    db.add(entry)
    await db.flush()
    return entry
