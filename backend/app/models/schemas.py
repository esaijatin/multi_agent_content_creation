from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    AWAITING_REVISION = "awaiting_revision"
    REVISING = "revising"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# --- Auth ---


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str

    model_config = {"from_attributes": True}


# --- Projects ---


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Workflows ---

_BLOCKED_PROMPT_PATTERNS = (
    "ignore previous",
    "ignore all previous",
    "system:",
    "you are now",
    "disregard instructions",
    "jailbreak",
)


class ContentRequest(BaseModel):
    """Validated user intent for content creation workflows."""

    prompt: str = Field(..., min_length=10, max_length=8000)
    platform: str = Field(..., pattern=r"^(youtube|tiktok|instagram|linkedin|podcast|blog)$")
    audience: str = Field(..., min_length=3, max_length=500)
    tone: str = Field(default="professional", max_length=100)
    complexity: str = Field(default="medium", pattern=r"^(low|medium|high)$")

    @field_validator("prompt")
    @classmethod
    def sanitize_prompt(cls, v: str) -> str:
        lower = v.lower()
        for phrase in _BLOCKED_PROMPT_PATTERNS:
            if phrase in lower:
                raise ValueError(f"Prompt contains disallowed pattern: {phrase}")
        return v.strip()


class WorkflowStartRequest(BaseModel):
    project_id: UUID
    content_request: ContentRequest


class WorkflowResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: WorkflowStatus
    current_stage: str | None
    iteration_count: int
    orchestrator_thread_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowStateResponse(BaseModel):
    workflow_id: UUID
    status: WorkflowStatus
    current_stage: str | None
    iteration_count: int
    token_usage_total: dict[str, int] = Field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    state: dict[str, Any] | None


class WorkflowLogEntry(BaseModel):
    timestamp: datetime
    stage: str
    agent: str | None
    message: str
    duration_ms: int | None = None
    token_usage: dict[str, int] = Field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    approved: bool
    feedback: str | None = Field(None, max_length=5000)


class ReviseRequest(BaseModel):
    feedback: str = Field(..., min_length=10, max_length=5000)
    target_stage: str | None = Field(
        None,
        description="Optional stage to rerun from (partial rerun)",
    )
