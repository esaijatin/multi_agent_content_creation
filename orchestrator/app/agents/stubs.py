"""Phase 2 stub agents — research, knowledge, narrative, critique, revision, approval."""

from typing import Any

from app.agents.base import run_agent_step
from app.config import get_settings
from app.state.workflow_state import WorkflowState


async def _stub_step(
    state: WorkflowState,
    *,
    stage: str,
    agent: str,
    next_stage: str,
    payload: dict[str, Any],
    message: str,
) -> dict[str, Any]:
    return {
        **payload,
        "current_stage": next_stage,
        "_log_message": message,
    }


async def _research(state: WorkflowState) -> dict[str, Any]:
    plan = state.get("planner_output", {})
    topics = plan.get("required_research_topics", ["general context"])
    return await _stub_step(
        state,
        stage="research",
        agent="research",
        next_stage="knowledge_consolidation",
        payload={
            "research_summary": {
                "topics": topics,
                "sources": [],
                "key_concepts": topics[:5],
                "note": "Research stub — Phase 3 implements RAG",
            },
        },
        message="Research stub completed (topics from planner)",
    )


async def _knowledge(state: WorkflowState) -> dict[str, Any]:
    research = state.get("research_summary", {})
    return await _stub_step(
        state,
        stage="knowledge_consolidation",
        agent="knowledge_consolidation",
        next_stage="narrative_strategy",
        payload={
            "knowledge_base": {
                "hierarchy": {"root": research.get("key_concepts", [])},
                "deduplicated_facts": research.get("key_concepts", []),
            },
        },
        message="Knowledge consolidated",
    )


async def _narrative(state: WorkflowState) -> dict[str, Any]:
    plan = state.get("planner_output", {})
    goals = plan.get("narrative_goals", ["engage audience", "deliver value"])
    return await _stub_step(
        state,
        stage="narrative_strategy",
        agent="narrative_strategist",
        next_stage="draft_writer",
        payload={
            "narrative_outline": {
                "hook": f"Address {plan.get('target_audience', 'viewers')} with a compelling opening",
                "acts": goals,
                "cta": "Subscribe / follow CTA",
                "pacing": plan.get("workflow_strategy", "steady build"),
            },
        },
        message="Narrative outline created",
    )


async def _critique(state: WorkflowState) -> dict[str, Any]:
    critiques = [
        {"agent": "fact_checker", "score": 0.8, "issues": [], "recommendations": []},
        {"agent": "engagement_critic", "score": 0.75, "issues": [], "recommendations": []},
        {"agent": "style_critic", "score": 0.85, "issues": [], "recommendations": []},
        {"agent": "platform_optimizer", "score": 0.78, "issues": [], "recommendations": []},
    ]
    avg = sum(c["score"] for c in critiques) / len(critiques)
    settings = get_settings()
    revision_required = avg < settings.critique_score_threshold
    next_stage = "revision_loop" if revision_required else "approval"
    return await _stub_step(
        state,
        stage="critique_panel",
        agent="critique_panel",
        next_stage=next_stage,
        payload={
            "critiques": critiques,
            "aggregated_feedback": {
                "average_score": avg,
                "revision_required": revision_required,
            },
        },
        message=f"Critique panel complete (avg={avg:.2f})",
    )


async def _revision(state: WorkflowState) -> dict[str, Any]:
    settings = get_settings()
    iteration = state.get("iteration_count", 0) + 1
    feedback = state.get("aggregated_feedback", {})
    avg = feedback.get("average_score", 0)

    if iteration >= settings.max_revision_iterations or avg >= settings.critique_score_threshold:
        return await _stub_step(
            state,
            stage="revision_loop",
            agent="revision_loop",
            next_stage="approval",
            payload={
                "iteration_count": iteration,
                "approval_pending": True,
                "status": "awaiting_approval",
                "final_output": state.get("draft", ""),
            },
            message="Revision threshold met — awaiting approval",
        )

    draft = state.get("draft", "") + f"\n\n<!-- Revision {iteration} placeholder -->"
    return await _stub_step(
        state,
        stage="revision_loop",
        agent="revision_loop",
        next_stage="critique_panel",
        payload={"draft": draft, "iteration_count": iteration},
        message=f"Revision iteration {iteration}",
    )


async def _approval(state: WorkflowState) -> dict[str, Any]:
    if state.get("approved"):
        return await _stub_step(
            state,
            stage="approval",
            agent="orchestrator",
            next_stage="completed",
            payload={
                "status": "completed",
                "current_stage": "completed",
                "final_output": state.get("draft", state.get("final_output", "")),
            },
            message="Workflow approved and completed",
        )
    return await _stub_step(
        state,
        stage="approval",
        agent="orchestrator",
        next_stage="approval",
        payload={"approval_pending": True, "status": "awaiting_approval"},
        message="Awaiting human approval",
    )


async def run_research(state: WorkflowState) -> dict[str, Any]:
    return await run_agent_step(state, stage="research", agent="research", fn=_research)


async def run_knowledge_consolidation(state: WorkflowState) -> dict[str, Any]:
    return await run_agent_step(
        state, stage="knowledge_consolidation", agent="knowledge_consolidation", fn=_knowledge
    )


async def run_narrative_strategist(state: WorkflowState) -> dict[str, Any]:
    return await run_agent_step(
        state, stage="narrative_strategy", agent="narrative_strategist", fn=_narrative
    )


async def run_critique_panel(state: WorkflowState) -> dict[str, Any]:
    return await run_agent_step(state, stage="critique_panel", agent="critique_panel", fn=_critique)


async def run_revision_loop(state: WorkflowState) -> dict[str, Any]:
    return await run_agent_step(state, stage="revision_loop", agent="revision_loop", fn=_revision)


async def run_approval_gate(state: WorkflowState) -> dict[str, Any]:
    return await run_agent_step(state, stage="approval", agent="orchestrator", fn=_approval)
