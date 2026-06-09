from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services.execution_service import get_execution_service
from app.services.model_service import get_model_service
from app.services.state_manager import get_state_manager, init_redis

router = APIRouter()


async def verify_internal_key(
    x_internal_api_key: str | None = Header(None),
) -> None:
    settings = get_settings()
    if x_internal_api_key != settings.orchestrator_internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )


class StartWorkflowRequest(BaseModel):
    workflow_id: str = Field(..., min_length=1, max_length=64)
    payload: dict[str, Any]


class ApproveRequest(BaseModel):
    approved: bool
    feedback: str | None = Field(None, max_length=5000)


class ReviseRequest(BaseModel):
    feedback: str = Field(..., min_length=10, max_length=5000)
    target_stage: str | None = Field(None, max_length=100)


@router.get("/health")
async def health() -> dict[str, Any]:
    redis_ok = False
    ollama_ok = False
    ollama_detail: dict[str, Any] = {}
    try:
        client = await init_redis()
        redis_ok = await client.ping()
    except Exception as exc:
        redis_ok = False
        ollama_detail["redis_error"] = str(exc)

    try:
        ollama_detail = await get_model_service().health_check()
        ollama_ok = True
    except Exception as exc:
        ollama_detail = {"status": "unavailable", "error": str(exc)}

    ready = redis_ok
    return {
        "status": "healthy" if ready else "degraded",
        "service": "orchestrator",
        "redis": redis_ok,
        "ollama": ollama_ok,
        "ollama_detail": ollama_detail,
        "ready": ready,
    }


@router.get("/ready")
async def ready() -> dict[str, str]:
    try:
        client = await init_redis()
        if await client.ping():
            return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Not ready: {exc}") from exc
    raise HTTPException(status_code=503, detail="Redis not ready")


@router.post("/internal/workflow/start", dependencies=[Depends(verify_internal_key)])
async def start_workflow(body: StartWorkflowRequest) -> dict[str, Any]:
    return await get_execution_service().enqueue(body.workflow_id, body.payload)


@router.get("/internal/workflow/{thread_id}/state", dependencies=[Depends(verify_internal_key)])
async def get_workflow_state(thread_id: str) -> dict[str, Any]:
    return await get_execution_service().get_state(thread_id)


@router.get("/internal/workflow/{thread_id}/events", dependencies=[Depends(verify_internal_key)])
async def get_workflow_events(thread_id: str) -> dict[str, Any]:
    events = await get_execution_service().get_events(thread_id)
    return {"thread_id": thread_id, "events": events}


@router.post("/internal/workflow/{thread_id}/approve", dependencies=[Depends(verify_internal_key)])
async def approve_workflow(thread_id: str, body: ApproveRequest) -> dict[str, Any]:
    return await get_execution_service().approve(thread_id, body.approved, body.feedback)


@router.post("/internal/workflow/{thread_id}/revise", dependencies=[Depends(verify_internal_key)])
async def revise_workflow(thread_id: str, body: ReviseRequest) -> dict[str, Any]:
    return await get_execution_service().revise(thread_id, body.feedback, body.target_stage)
