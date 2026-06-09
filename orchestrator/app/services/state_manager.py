"""Redis-backed execution metadata and event history."""

from datetime import datetime, timezone
from typing import Any

import redis.asyncio as redis
import structlog

from app.config import get_settings
from app.schemas.workflow import ExecutionMetadata, ExecutionStatus, OrchestrationEvent
from app.utils.exceptions import WorkflowNotFoundError

logger = structlog.get_logger(__name__)


class StateManager:
    def __init__(self, client: redis.Redis) -> None:
        self._redis = client

    @staticmethod
    def _meta_key(thread_id: str) -> str:
        return f"astraos:workflow:meta:{thread_id}"

    @staticmethod
    def _events_key(thread_id: str) -> str:
        return f"astraos:workflow:events:{thread_id}"

    @staticmethod
    def _active_key() -> str:
        return "astraos:workflow:active"

    async def create_execution(
        self,
        *,
        workflow_id: str,
        thread_id: str,
    ) -> ExecutionMetadata:
        now = datetime.now(timezone.utc)
        meta = ExecutionMetadata(
            workflow_id=workflow_id,
            thread_id=thread_id,
            status=ExecutionStatus.QUEUED,
            current_stage="queued",
            started_at=now,
            updated_at=now,
        )
        await self._save_meta(meta)
        await self._redis.sadd(self._active_key(), thread_id)
        return meta

    async def get_meta(self, thread_id: str) -> ExecutionMetadata:
        raw = await self._redis.get(self._meta_key(thread_id))
        if not raw:
            raise WorkflowNotFoundError(thread_id)
        return ExecutionMetadata.model_validate_json(raw)

    async def update_meta(self, thread_id: str, **updates: Any) -> ExecutionMetadata:
        meta = await self.get_meta(thread_id)
        data = meta.model_dump()
        data.update(updates)
        data["updated_at"] = datetime.now(timezone.utc)
        updated = ExecutionMetadata.model_validate(data)
        await self._save_meta(updated)
        return updated

    async def _save_meta(self, meta: ExecutionMetadata) -> None:
        await self._redis.set(
            self._meta_key(meta.thread_id),
            meta.model_dump_json(),
        )

    async def append_event(self, thread_id: str, event: OrchestrationEvent) -> None:
        await self._redis.rpush(
            self._events_key(thread_id),
            event.model_dump_json(),
        )
        meta = await self.get_meta(thread_id)
        totals = dict(meta.token_usage_total)
        for k, v in event.token_usage.items():
            totals[k] = totals.get(k, 0) + v
        await self.update_meta(thread_id, token_usage_total=totals)

    async def list_events(self, thread_id: str, limit: int = 200) -> list[OrchestrationEvent]:
        try:
            await self.get_meta(thread_id)
        except WorkflowNotFoundError:
            return []
        raw_items = await self._redis.lrange(self._events_key(thread_id), -limit, -1)
        return [OrchestrationEvent.model_validate_json(item) for item in raw_items]

    async def list_active_threads(self) -> list[str]:
        members = await self._redis.smembers(self._active_key())
        return [m.decode() if isinstance(m, bytes) else m for m in members]

    async def mark_finished(self, thread_id: str, status: ExecutionStatus) -> None:
        """Finalize workflow; remove from active set only when terminal."""
        updates: dict[str, Any] = {"status": status, "updated_at": datetime.now(timezone.utc)}
        if status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
            updates["completed_at"] = datetime.now(timezone.utc)
        await self.update_meta(thread_id, **updates)
        if status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
            await self._redis.srem(self._active_key(), thread_id)

    async def merge_token_usage(self, thread_id: str, usage: dict[str, int]) -> None:
        meta = await self.get_meta(thread_id)
        totals = dict(meta.token_usage_total)
        for k, v in usage.items():
            totals[k] = totals.get(k, 0) + v
        await self.update_meta(thread_id, token_usage_total=totals)


_state_manager: StateManager | None = None
_redis_client: redis.Redis | None = None


async def init_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def close_redis() -> None:
    global _redis_client, _state_manager
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
    _state_manager = None


def get_state_manager() -> StateManager:
    global _state_manager
    if _state_manager is None:
        if _redis_client is None:
            raise RuntimeError("Redis not initialized — call init_redis() in lifespan")
        _state_manager = StateManager(_redis_client)
    return _state_manager
