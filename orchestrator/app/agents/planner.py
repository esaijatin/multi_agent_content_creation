"""Planner Agent — LLM-powered structured execution planning."""

from typing import Any

from app.agents.base import run_agent_step
from app.config import get_settings
from app.schemas.planner import PlannerOutput
from app.services.model_service import get_model_service
from app.state.workflow_state import WorkflowState, planner_to_state


PLANNER_SYSTEM = """You are the Planning Agent for AstraOS, an enterprise content orchestration platform.
Analyze the user request and produce a strategic execution plan as JSON only.
Do not write the final script. Focus on strategy, audience, risks, and research topics."""


async def _plan(state: WorkflowState) -> dict[str, Any]:
    request = state.get("content_request", {})
    prompt = f"""Analyze this content request and return a structured plan.

User prompt: {request.get('prompt', '')}
Platform: {request.get('platform', 'youtube')}
Audience hint: {request.get('audience', 'general')}
Tone: {request.get('tone', 'professional')}
Complexity: {request.get('complexity', 'medium')}

Return JSON matching the PlannerOutput schema."""

    model = get_model_service()
    settings = get_settings()
    output, usage = await model.structured_generate(
        role=settings.model_role_planner,
        prompt=prompt,
        schema=PlannerOutput,
        system=PLANNER_SYSTEM,
        max_attempts=settings.planner_max_retries,
        temperature=0.3,
    )

    plan_dict = planner_to_state(output)
    execution_plan = {
        "platform": output.platform,
        "audience": output.target_audience,
        "complexity": output.complexity_level.value,
        "stages": [
            "research",
            "knowledge_consolidation",
            "narrative_strategy",
            "draft_writer",
            "critique_panel",
            "revision_loop",
            "approval",
        ],
        "estimated_duration_minutes": output.estimated_duration_minutes,
        "workflow_strategy": output.workflow_strategy,
    }

    return {
        "planner_output": plan_dict,
        "execution_plan": execution_plan,
        "current_stage": "research",
        "status": "running",
        "_token_usage": usage,
        "_log_message": "Planner produced structured execution plan",
        "_log_metadata": {"content_type": output.content_type, "risk_flags": output.risk_flags},
    }


async def run_planner(state: WorkflowState) -> dict[str, Any]:
    return await run_agent_step(state, stage="planner", agent="planner", fn=_plan)
