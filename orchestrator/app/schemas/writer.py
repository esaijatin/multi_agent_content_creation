from pydantic import BaseModel, Field


class ScriptSection(BaseModel):
    heading: str
    content: str
    estimated_seconds: int | None = None


class WriterOutput(BaseModel):
    """Structured draft output from the Writer agent."""

    title: str
    hook: str
    sections: list[ScriptSection]
    transitions: list[str] = Field(default_factory=list)
    conclusion: str
    cta_placeholder: str
    markdown: str = Field(..., description="Full assembled markdown script")

    model_config = {"extra": "forbid"}
