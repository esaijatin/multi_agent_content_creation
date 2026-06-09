import uuid

from fastapi import APIRouter, status

from app.core.dependencies import DbSession, OperatorUser
from app.models.schemas import (
    ApprovalRequest,
    ReviseRequest,
    WorkflowLogEntry,
    WorkflowResponse,
    WorkflowStartRequest,
    WorkflowStateResponse,
)
from app.services.orchestrator_client import get_orchestrator_client
from app.services.workflow_service import (
    approve_workflow,
    create_workflow,
    get_workflow,
    get_workflow_state,
    list_workflow_logs,
    revise_workflow,
)


router = APIRouter(prefix="/workflow", tags=["workflows"])


@router.post("/start", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def start_workflow(
    body: WorkflowStartRequest,
    db: DbSession,
    current_user: OperatorUser,
) -> WorkflowResponse:
    return await create_workflow(
        db,
        request=body,
        actor_id=current_user.sub,
        orchestrator=get_orchestrator_client(),
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_endpoint(
    workflow_id: uuid.UUID,
    db: DbSession,
    current_user: OperatorUser,
) -> WorkflowResponse:
    workflow = await get_workflow(db, workflow_id, current_user.sub)
    return WorkflowResponse.model_validate(workflow)


@router.get("/{workflow_id}/state", response_model=WorkflowStateResponse)
async def get_workflow_state_endpoint(
    workflow_id: uuid.UUID,
    db: DbSession,
    current_user: OperatorUser,
) -> WorkflowStateResponse:
    return await get_workflow_state(
        db, workflow_id, current_user.sub, get_orchestrator_client()
    )


@router.get("/{workflow_id}/logs", response_model=list[WorkflowLogEntry])
async def get_workflow_logs(
    workflow_id: uuid.UUID,
    db: DbSession,
    current_user: OperatorUser,
) -> list[WorkflowLogEntry]:
    logs = await list_workflow_logs(db, workflow_id, current_user.sub)
    return [WorkflowLogEntry(**log) for log in logs]


@router.post("/{workflow_id}/approve", response_model=WorkflowResponse)
async def approve_workflow_endpoint(
    workflow_id: uuid.UUID,
    body: ApprovalRequest,
    db: DbSession,
    current_user: OperatorUser,
) -> WorkflowResponse:
    return await approve_workflow(
        db,
        workflow_id,
        body,
        current_user.sub,
        get_orchestrator_client(),
    )


@router.post("/{workflow_id}/revise", response_model=WorkflowResponse)
async def revise_workflow_endpoint(
    workflow_id: uuid.UUID,
    body: ReviseRequest,
    db: DbSession,
    current_user: OperatorUser,
) -> WorkflowResponse:
    return await revise_workflow(
        db,
        workflow_id,
        body,
        current_user.sub,
        get_orchestrator_client(),
    )
