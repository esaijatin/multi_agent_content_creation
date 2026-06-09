from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_REVISION = "awaiting_revision"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class OrchestrationEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())
    stage: str
    agent: str | None = None
    message: str
    duration_ms: int | None = None
    token_usage: dict[str, int] = Field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionMetadata(BaseModel):
    workflow_id: str
    thread_id: str
    status: ExecutionStatus
    current_stage: str | None = None
    iteration_count: int = 0
    started_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    retry_count: int = 0
    token_usage_total: dict[str, int] = Field(default_factory=dict)
