from enum import Enum

from pydantic import BaseModel, Field


class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PlannerOutput(BaseModel):
    """Strict structured output from the Planner agent."""

    content_type: str = Field(..., description="e.g. video_script, blog_post, podcast_outline")
    platform: str
    target_audience: str
    tone: str
    complexity_level: ComplexityLevel
    estimated_duration_minutes: int = Field(..., ge=1, le=180)
    required_research_topics: list[str] = Field(default_factory=list)
    workflow_strategy: str = Field(
        ...,
        description="High-level execution approach for downstream agents",
    )
    risk_flags: list[str] = Field(default_factory=list)
    narrative_goals: list[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}
