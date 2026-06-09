"""LangGraph Redis checkpointer lifecycle."""

from typing import Any

import structlog
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from app.config import get_settings
from app.utils.exceptions import CheckpointError

logger = structlog.get_logger(__name__)

_saver: AsyncRedisSaver | None = None
_saver_cm: Any = None


async def init_checkpointer() -> AsyncRedisSaver:
    """Initialize and return the shared AsyncRedisSaver."""
    global _saver, _saver_cm
    if _saver is not None:
        return _saver

    settings = get_settings()
    try:
        _saver_cm = AsyncRedisSaver.from_conn_string(settings.redis_url)
        _saver = await _saver_cm.__aenter__()
        await _saver.asetup()
        logger.info("redis_checkpointer_ready", redis_url=settings.redis_url.split("@")[-1])
        return _saver
    except Exception as exc:
        raise CheckpointError(f"Failed to initialize Redis checkpointer: {exc}") from exc


async def close_checkpointer() -> None:
    global _saver, _saver_cm
    if _saver_cm is not None:
        await _saver_cm.__aexit__(None, None, None)
        _saver = None
        _saver_cm = None
        logger.info("redis_checkpointer_closed")


def get_checkpointer() -> AsyncRedisSaver:
    if _saver is None:
        raise CheckpointError("Checkpointer not initialized")
    return _saver
