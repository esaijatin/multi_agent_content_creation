"""Draft Writer Agent — converts outline into polished markdown script."""

import json
from typing import Any

from app.agents.base import run_agent_step
from app.config import get_settings
from app.schemas.writer import WriterOutput
from app.services.model_service import get_model_service
from app.state.workflow_state import WorkflowState, writer_to_state


WRITER_SYSTEM = """You are the Draft Writer Agent for AstraOS.
Write a polished content script in markdown. Do not research or critique.
Follow the narrative outline and planner strategy. Output valid JSON matching WriterOutput schema.
The markdown field must contain the full script with headings."""


async def _write(state: WorkflowState) -> dict[str, Any]:
    request = state.get("content_request", {})
    plan = state.get("planner_output") or state.get("execution_plan", {})
    outline = state.get("narrative_outline", {})

    prompt = f"""Write the first draft script.

User prompt: {request.get('prompt', '')}
Platform: {request.get('platform', 'youtube')}
Tone: {request.get('tone', plan.get('tone', 'professional'))}
Target audience: {plan.get('target_audience', request.get('audience', 'general'))}
Workflow strategy: {plan.get('workflow_strategy', '')}
Narrative outline: {json.dumps(outline, indent=2)}

Requirements:
- Strong hook
- Clear sections with headings
- Smooth transitions
- Conclusion and CTA placeholder
- Return JSON with title, hook, sections, transitions, conclusion, cta_placeholder, markdown"""

    model = get_model_service()
    settings = get_settings()
    output, usage = await model.structured_generate(
        role=settings.model_role_writer,
        prompt=prompt,
        schema=WriterOutput,
        system=WRITER_SYSTEM,
        max_attempts=settings.writer_max_retries,
        temperature=0.6,
    )

    writer_dict = writer_to_state(output)
    return {
        "writer_output": writer_dict,
        "draft": output.markdown,
        "current_stage": "critique_panel",
        "status": "running",
        "_token_usage": usage,
        "_log_message": "Draft writer produced markdown script",
        "_log_metadata": {"title": output.title, "sections": len(output.sections)},
    }


async def run_draft_writer(state: WorkflowState) -> dict[str, Any]:
    return await run_agent_step(state, stage="draft_writer", agent="draft_writer", fn=_write)
