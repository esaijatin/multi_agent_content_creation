import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from app.logging.orchestration import append_log_entry, log_event
from app.services.state_manager import get_state_manager
from app.state.workflow_state import WorkflowState

T = TypeVar("T")


async def run_agent_step(
    state: WorkflowState,
    *,
    stage: str,
    agent: str,
    fn: Callable[[WorkflowState], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    """Wrap agent execution with timing, logging, and event persistence."""
    thread_id = state.get("thread_id", "")
    state_manager = get_state_manager()
    start = time.perf_counter()
    error: str | None = None
    result: dict[str, Any] = {}

    try:
        result = await fn(state)
    except Exception as exc:
        error = str(exc)
        result = {
            "errors": state.get("errors", []) + [f"{agent}: {error}"],
            "status": "failed",
        }
        raise
    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        usage = result.pop("_token_usage", {})
        event = log_event(
            stage=stage,
            agent=agent,
            message=result.get("_log_message", f"{agent} completed"),
            duration_ms=duration_ms,
            token_usage=usage,
            error=error,
            metadata=result.get("_log_metadata"),
        )
        if thread_id:
            await state_manager.append_event(thread_id, event)
            if usage:
                await state_manager.merge_token_usage(thread_id, usage)

        logs = append_log_entry(state, event)
        result["execution_logs"] = logs

    return result
