import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AuditLog, Project, Workflow, WorkflowEvent, WorkflowStatus
from app.models.schemas import (
    ApprovalRequest,
    ReviseRequest,
    WorkflowResponse,
    WorkflowStartRequest,
    WorkflowStateResponse,
    WorkflowStatus as SchemaStatus,
)
from app.services.audit import write_audit_log
from app.services.orchestrator_client import OrchestratorClient
from app.services.workflow_events import persist_orchestrator_events


async def _verify_project_access(
    db: AsyncSession,
    project_id: uuid.UUID,
    actor_id: str,
) -> Project:
    project = await db.get(Project, project_id)
    if not project or str(project.owner_id) != actor_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


async def _verify_workflow_access(
    db: AsyncSession,
    workflow_id: uuid.UUID,
    actor_id: str,
) -> Workflow:
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    project = await db.get(Project, workflow.project_id)
    if not project or str(project.owner_id) != actor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return workflow


def _map_remote_status(remote_status: str) -> str:
    mapping = {
        "queued": WorkflowStatus.QUEUED.value,
        "running": WorkflowStatus.RUNNING.value,
        "awaiting_approval": WorkflowStatus.AWAITING_APPROVAL.value,
        "awaiting_revision": WorkflowStatus.AWAITING_REVISION.value,
        "revising": WorkflowStatus.REVISING.value,
        "completed": WorkflowStatus.COMPLETED.value,
        "failed": WorkflowStatus.FAILED.value,
    }
    return mapping.get(remote_status, WorkflowStatus.RUNNING.value)


async def create_workflow(
    db: AsyncSession,
    *,
    request: WorkflowStartRequest,
    actor_id: str,
    orchestrator: OrchestratorClient,
) -> WorkflowResponse:
    await _verify_project_access(db, request.project_id, actor_id)

    workflow = Workflow(
        project_id=request.project_id,
        status=WorkflowStatus.QUEUED.value,
        current_stage="queued",
        input_payload=request.content_request.model_dump(),
        started_at=datetime.now(timezone.utc),
    )
    db.add(workflow)
    await db.flush()

    await write_audit_log(
        db,
        actor_id=actor_id,
        action="workflow.queued",
        resource_type="workflow",
        resource_id=str(workflow.id),
        workflow_id=workflow.id,
        details={
            "project_id": str(request.project_id),
            "stage": "queued",
            "agent": "orchestrator",
        },
    )

    try:
        result = await orchestrator.start_workflow(
            workflow.id,
            request.content_request.model_dump(),
        )
        workflow.orchestrator_thread_id = result.get("thread_id")
        workflow.status = _map_remote_status(result.get("status", "queued"))
        workflow.current_stage = result.get("current_stage", "queued")
    except Exception as exc:
        workflow.status = WorkflowStatus.FAILED.value
        workflow.error_message = str(exc)
        await write_audit_log(
            db,
            actor_id="system",
            action="workflow.start_failed",
            resource_type="workflow",
            resource_id=str(workflow.id),
            workflow_id=workflow.id,
            details={"error": str(exc), "stage": "queued"},
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Orchestrator failed to queue workflow",
        ) from exc

    await db.refresh(workflow)
    return WorkflowResponse.model_validate(workflow)


async def get_workflow(
    db: AsyncSession,
    workflow_id: uuid.UUID,
    actor_id: str,
) -> Workflow:
    return await _verify_workflow_access(db, workflow_id, actor_id)


async def _sync_from_orchestrator(
    db: AsyncSession,
    workflow: Workflow,
    orchestrator: OrchestratorClient,
) -> dict[str, Any]:
    if not workflow.orchestrator_thread_id:
        return {}

    remote = await orchestrator.get_state(workflow.orchestrator_thread_id)
    workflow.status = _map_remote_status(remote.get("status", workflow.status))
    workflow.current_stage = remote.get("current_stage", workflow.current_stage)
    workflow.iteration_count = remote.get("iteration_count", workflow.iteration_count)
    workflow.state_snapshot = remote.get("state")
    workflow.token_usage_total = remote.get("token_usage_total", workflow.token_usage_total or {})
    workflow.error_message = remote.get("error")

    if remote.get("status") in ("completed", "failed"):
        workflow.completed_at = datetime.now(timezone.utc)

    try:
        events_payload = await orchestrator.get_events(workflow.orchestrator_thread_id)
        await persist_orchestrator_events(db, workflow.id, events_payload.get("events", []))
    except Exception:
        pass
    return remote


async def get_workflow_state(
    db: AsyncSession,
    workflow_id: uuid.UUID,
    actor_id: str,
    orchestrator: OrchestratorClient,
) -> WorkflowStateResponse:
    workflow = await _verify_workflow_access(db, workflow_id, actor_id)

    try:
        remote = await _sync_from_orchestrator(db, workflow, orchestrator)
    except Exception:
        remote = {}

    return WorkflowStateResponse(
        workflow_id=workflow.id,
        status=SchemaStatus(workflow.status),
        current_stage=workflow.current_stage,
        iteration_count=workflow.iteration_count,
        token_usage_total=workflow.token_usage_total or {},
        started_at=workflow.started_at,
        completed_at=workflow.completed_at,
        error_message=workflow.error_message,
        state=workflow.state_snapshot,
    )


async def approve_workflow(
    db: AsyncSession,
    workflow_id: uuid.UUID,
    body: ApprovalRequest,
    actor_id: str,
    orchestrator: OrchestratorClient,
) -> WorkflowResponse:
    workflow = await _verify_workflow_access(db, workflow_id, actor_id)
    if not workflow.orchestrator_thread_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No orchestrator thread")

    await orchestrator.approve(
        workflow.orchestrator_thread_id,
        body.approved,
        body.feedback,
    )
    workflow.status = (
        WorkflowStatus.COMPLETED.value if body.approved else WorkflowStatus.AWAITING_REVISION.value
    )
    if body.approved:
        workflow.completed_at = datetime.now(timezone.utc)

    await write_audit_log(
        db,
        actor_id=actor_id,
        action="workflow.approve" if body.approved else "workflow.reject",
        resource_type="workflow",
        resource_id=str(workflow.id),
        workflow_id=workflow.id,
        details={"feedback": body.feedback, "stage": "approval"},
    )

    await db.refresh(workflow)
    return WorkflowResponse.model_validate(workflow)


async def revise_workflow(
    db: AsyncSession,
    workflow_id: uuid.UUID,
    body: ReviseRequest,
    actor_id: str,
    orchestrator: OrchestratorClient,
) -> WorkflowResponse:
    workflow = await _verify_workflow_access(db, workflow_id, actor_id)
    if not workflow.orchestrator_thread_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No orchestrator thread")

    await orchestrator.revise(
        workflow.orchestrator_thread_id,
        body.feedback,
        body.target_stage,
    )
    workflow.status = WorkflowStatus.AWAITING_REVISION.value

    await write_audit_log(
        db,
        actor_id=actor_id,
        action="workflow.revise",
        resource_type="workflow",
        resource_id=str(workflow.id),
        workflow_id=workflow.id,
        details={"target_stage": body.target_stage, "stage": "revision"},
    )

    await db.refresh(workflow)
    return WorkflowResponse.model_validate(workflow)


async def list_workflow_logs(db: AsyncSession, workflow_id: uuid.UUID, actor_id: str) -> list[dict[str, Any]]:
    workflow = await _verify_workflow_access(db, workflow_id, actor_id)

    result = await db.execute(
        select(WorkflowEvent)
        .where(WorkflowEvent.workflow_id == workflow.id)
        .order_by(WorkflowEvent.created_at.asc())
    )
    events = result.scalars().all()
    if events:
        return [
            {
                "timestamp": ev.created_at,
                "stage": ev.stage,
                "agent": ev.agent,
                "message": ev.message,
                "duration_ms": ev.duration_ms,
                "token_usage": ev.token_usage or {},
                "error": ev.error,
                "metadata": ev.metadata_ or {},
            }
            for ev in events
        ]

    # Fallback to audit logs
    audit_result = await db.execute(
        select(AuditLog)
        .where(AuditLog.workflow_id == workflow.id)
        .order_by(AuditLog.created_at.desc())
    )
    logs = audit_result.scalars().all()
    return [
        {
            "timestamp": log.created_at,
            "stage": (log.details or {}).get("stage", "system"),
            "agent": (log.details or {}).get("agent"),
            "message": log.action,
            "metadata": log.details or {},
        }
        for log in logs
    ]
