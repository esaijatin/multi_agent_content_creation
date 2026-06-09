"""LangGraph content workflow — deterministic multi-agent pipeline."""

from typing import Literal

from langgraph.graph import END, StateGraph

from app.agents.planner import run_planner
from app.agents.stubs import (
    run_approval_gate,
    run_critique_panel,
    run_knowledge_consolidation,
    run_narrative_strategist,
    run_research,
    run_revision_loop,
)
from app.agents.writer import run_draft_writer
from app.checkpoints.redis_checkpoint import get_checkpointer
from app.state.workflow_state import WorkflowState

_compiled_graph = None


def _route_after_critique(state: WorkflowState) -> Literal["revision_loop", "approval"]:
    feedback = state.get("aggregated_feedback", {})
    if feedback.get("revision_required"):
        return "revision_loop"
    return "approval"


def _route_after_revision(state: WorkflowState) -> Literal["critique_panel", "approval"]:
    if state.get("current_stage") == "critique_panel":
        return "critique_panel"
    return "approval"


def _route_approval(state: WorkflowState) -> Literal["approval", "__end__"]:
    if state.get("status") == "completed":
        return "__end__"
    return "approval"


def build_content_workflow() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("planner", run_planner)
    graph.add_node("research", run_research)
    graph.add_node("knowledge_consolidation", run_knowledge_consolidation)
    graph.add_node("narrative_strategy", run_narrative_strategist)
    graph.add_node("draft_writer", run_draft_writer)
    graph.add_node("critique_panel", run_critique_panel)
    graph.add_node("revision_loop", run_revision_loop)
    graph.add_node("approval", run_approval_gate)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "research")
    graph.add_edge("research", "knowledge_consolidation")
    graph.add_edge("knowledge_consolidation", "narrative_strategy")
    graph.add_edge("narrative_strategy", "draft_writer")
    graph.add_edge("draft_writer", "critique_panel")
    graph.add_conditional_edges("critique_panel", _route_after_critique)
    graph.add_conditional_edges("revision_loop", _route_after_revision)
    graph.add_conditional_edges("approval", _route_approval)

    return graph


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        checkpointer = get_checkpointer()
        _compiled_graph = build_content_workflow().compile(checkpointer=checkpointer)
    return _compiled_graph
