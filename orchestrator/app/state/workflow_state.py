"""Typed workflow state for LangGraph."""

from typing import Any, TypedDict

from app.schemas.planner import PlannerOutput
from app.schemas.writer import WriterOutput


class WorkflowState(TypedDict, total=False):
    workflow_id: str
    thread_id: str
    status: str
    current_stage: str
    iteration_count: int

    content_request: dict[str, Any]

    execution_plan: dict[str, Any]
    planner_output: dict[str, Any]
    research_summary: dict[str, Any]
    knowledge_base: dict[str, Any]
    narrative_outline: dict[str, Any]
    draft: str
    writer_output: dict[str, Any]
    critiques: list[dict[str, Any]]
    aggregated_feedback: dict[str, Any]
    final_output: str

    approval_pending: bool
    approved: bool
    human_feedback: str | None
    errors: list[str]
    execution_logs: list[dict[str, Any]]


def planner_to_state(output: PlannerOutput) -> dict[str, Any]:
    return output.model_dump()


def writer_to_state(output: WriterOutput) -> dict[str, Any]:
    return output.model_dump()
