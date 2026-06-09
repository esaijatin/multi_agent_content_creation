"""Async workflow execution, recovery, and lifecycle management."""

import asyncio
from typing import Any

import structlog

from app.logging.orchestration import log_event
from app.schemas.workflow import ExecutionStatus
from app.services.state_manager import get_state_manager
from app.state.workflow_state import WorkflowState
from app.utils.exceptions import OrchestratorError, WorkflowNotFoundError
from app.workflows.content_workflow import get_compiled_graph

logger = structlog.get_logger(__name__)

_running_tasks: dict[str, asyncio.Task] = {}


def _graph_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _sanitize_state(state: dict[str, Any]) -> dict[str, Any]:
    skip = {"execution_logs"}
    return {k: v for k, v in state.items() if k not in skip}


class ExecutionService:
    async def enqueue(self, workflow_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        thread_id = f"thread-{workflow_id}"
        state_manager = get_state_manager()

        await state_manager.create_execution(workflow_id=workflow_id, thread_id=thread_id)
        await state_manager.append_event(
            thread_id,
            log_event(stage="queued", agent="orchestrator", message="Workflow queued"),
        )

        task = asyncio.create_task(self._execute(thread_id, workflow_id, payload))
        _running_tasks[thread_id] = task
        task.add_done_callback(lambda t: _running_tasks.pop(thread_id, None))

        return {
            "thread_id": thread_id,
            "workflow_id": workflow_id,
            "status": ExecutionStatus.QUEUED.value,
            "current_stage": "queued",
        }

    async def _execute(
        self,
        thread_id: str,
        workflow_id: str,
        payload: dict[str, Any],
    ) -> None:
        state_manager = get_state_manager()
        await state_manager.update_meta(
            thread_id,
            status=ExecutionStatus.RUNNING,
            current_stage="planner",
        )

        initial: WorkflowState = {
            "workflow_id": workflow_id,
            "thread_id": thread_id,
            "status": "running",
            "current_stage": "planner",
            "iteration_count": 0,
            "content_request": payload,
            "critiques": [],
            "errors": [],
            "execution_logs": [],
            "approval_pending": False,
            "approved": False,
        }

        try:
            graph = get_compiled_graph()
            result = await graph.ainvoke(initial, config=_graph_config(thread_id))
            status = result.get("status", "running")
            exec_status = self._map_status(status)

            await state_manager.update_meta(
                thread_id,
                status=exec_status,
                current_stage=result.get("current_stage"),
                iteration_count=result.get("iteration_count", 0),
            )

            if exec_status == ExecutionStatus.FAILED:
                await state_manager.mark_finished(thread_id, exec_status)
            elif exec_status == ExecutionStatus.COMPLETED:
                await state_manager.mark_finished(thread_id, exec_status)
            else:
                await state_manager.update_meta(
                    thread_id,
                    status=exec_status,
                    current_stage=result.get("current_stage"),
                    iteration_count=result.get("iteration_count", 0),
                )

            logger.info(
                "workflow_execution_finished",
                thread_id=thread_id,
                status=exec_status.value,
            )
        except Exception as exc:
            logger.exception("workflow_execution_failed", thread_id=thread_id)
            await state_manager.update_meta(
                thread_id,
                status=ExecutionStatus.FAILED,
                error=str(exc),
                current_stage="failed",
            )
            await state_manager.mark_finished(thread_id, ExecutionStatus.FAILED)
            await state_manager.append_event(
                thread_id,
                log_event(
                    stage="system",
                    agent="orchestrator",
                    message="Workflow execution failed",
                    error=str(exc),
                ),
            )

    @staticmethod
    def _map_status(graph_status: str) -> ExecutionStatus:
        mapping = {
            "running": ExecutionStatus.RUNNING,
            "awaiting_approval": ExecutionStatus.AWAITING_APPROVAL,
            "revising": ExecutionStatus.AWAITING_REVISION,
            "completed": ExecutionStatus.COMPLETED,
            "failed": ExecutionStatus.FAILED,
        }
        return mapping.get(graph_status, ExecutionStatus.RUNNING)

    async def get_state(self, thread_id: str) -> dict[str, Any]:
        state_manager = get_state_manager()
        try:
            meta = await state_manager.get_meta(thread_id)
        except WorkflowNotFoundError:
            return {"error": "Thread not found", "thread_id": thread_id}

        graph_state: dict[str, Any] | None = None
        try:
            graph = get_compiled_graph()
            snapshot = await graph.aget_state(_graph_config(thread_id))
            if snapshot and snapshot.values:
                graph_state = _sanitize_state(dict(snapshot.values))
        except Exception as exc:
            logger.warning("checkpoint_state_read_failed", thread_id=thread_id, error=str(exc))

        return {
            "thread_id": thread_id,
            "workflow_id": meta.workflow_id,
            "status": meta.status.value,
            "current_stage": (
                graph_state.get("current_stage") if graph_state else None
            )
            or meta.current_stage,
            "iteration_count": graph_state.get("iteration_count", meta.iteration_count) if graph_state else meta.iteration_count,
            "token_usage_total": meta.token_usage_total,
            "started_at": meta.started_at.isoformat() if meta.started_at else None,
            "updated_at": meta.updated_at.isoformat() if meta.updated_at else None,
            "error": meta.error,
            "state": graph_state,
        }

    async def get_events(self, thread_id: str) -> list[dict[str, Any]]:
        events = await get_state_manager().list_events(thread_id)
        return [e.model_dump(mode="json") for e in events]

    async def approve(self, thread_id: str, approved: bool, feedback: str | None) -> dict[str, Any]:
        graph = get_compiled_graph()
        snapshot = await graph.aget_state(_graph_config(thread_id))
        if not snapshot or not snapshot.values:
            raise WorkflowNotFoundError(thread_id)

        state = dict(snapshot.values)
        state["approved"] = approved
        state["human_feedback"] = feedback

        if approved:
            state["status"] = "completed"
            state["current_stage"] = "completed"
            state["final_output"] = state.get("draft", "")
        else:
            state["status"] = "revising"
            state["current_stage"] = "revision_loop"
            state["approved"] = False

        await graph.aupdate_state(_graph_config(thread_id), state)
        state_manager = get_state_manager()
        exec_status = ExecutionStatus.COMPLETED if approved else ExecutionStatus.AWAITING_REVISION
        await state_manager.update_meta(thread_id, status=exec_status, current_stage=state["current_stage"])
        if approved:
            await state_manager.mark_finished(thread_id, ExecutionStatus.COMPLETED)

        if not approved:
            task = asyncio.create_task(graph.ainvoke(None, config=_graph_config(thread_id)))
            _running_tasks[thread_id] = task

        return {"thread_id": thread_id, "status": state["status"]}

    async def revise(self, thread_id: str, feedback: str, target_stage: str | None) -> dict[str, Any]:
        graph = get_compiled_graph()
        snapshot = await graph.aget_state(_graph_config(thread_id))
        if not snapshot or not snapshot.values:
            raise WorkflowNotFoundError(thread_id)

        state = dict(snapshot.values)
        state["human_feedback"] = feedback
        state["status"] = "revising"
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        if target_stage:
            state["current_stage"] = target_stage

        await graph.aupdate_state(_graph_config(thread_id), state)
        await get_state_manager().update_meta(
            thread_id,
            status=ExecutionStatus.AWAITING_REVISION,
            current_stage=state.get("current_stage"),
        )

        task = asyncio.create_task(graph.ainvoke(None, config=_graph_config(thread_id)))
        _running_tasks[thread_id] = task
        task.add_done_callback(lambda t: _running_tasks.pop(thread_id, None))

        return {"thread_id": thread_id, "status": "revising"}

    async def recover_interrupted(self) -> int:
        """Resume workflows that were running when orchestrator stopped."""
        state_manager = get_state_manager()
        active = await state_manager.list_active_threads()
        recovered = 0

        for thread_id in active:
            if thread_id in _running_tasks:
                continue
            try:
                meta = await state_manager.get_meta(thread_id)
            except WorkflowNotFoundError:
                continue

            if meta.status not in (ExecutionStatus.RUNNING, ExecutionStatus.QUEUED):
                continue

            logger.info("recovering_workflow", thread_id=thread_id)
            task = asyncio.create_task(self._resume(thread_id))
            _running_tasks[thread_id] = task
            task.add_done_callback(lambda t, tid=thread_id: _running_tasks.pop(tid, None))
            recovered += 1

        return recovered

    async def _resume(self, thread_id: str) -> None:
        try:
            graph = get_compiled_graph()
            await graph.ainvoke(None, config=_graph_config(thread_id))
        except Exception as exc:
            logger.exception("workflow_resume_failed", thread_id=thread_id)
            await get_state_manager().update_meta(
                thread_id,
                status=ExecutionStatus.FAILED,
                error=str(exc),
            )


_execution_service: ExecutionService | None = None


def get_execution_service() -> ExecutionService:
    global _execution_service
    if _execution_service is None:
        _execution_service = ExecutionService()
    return _execution_service
