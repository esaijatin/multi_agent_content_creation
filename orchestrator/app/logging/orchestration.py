from datetime import datetime, timezone
from typing import Any

import structlog

from app.schemas.workflow import OrchestrationEvent

logger = structlog.get_logger("orchestration")


def log_event(
    *,
    stage: str,
    agent: str | None,
    message: str,
    duration_ms: int | None = None,
    token_usage: dict[str, int] | None = None,
    error: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> OrchestrationEvent:
    event = OrchestrationEvent(
        timestamp=datetime.now(timezone.utc),
        stage=stage,
        agent=agent,
        message=message,
        duration_ms=duration_ms,
        token_usage=token_usage or {},
        error=error,
        metadata=metadata or {},
    )
    log_kwargs = {
        "stage": stage,
        "agent": agent,
        "message": message,
        "duration_ms": duration_ms,
    }
    if error:
        logger.error("orchestration_event", error=error, **log_kwargs)
    else:
        logger.info("orchestration_event", **log_kwargs)
    return event


def append_log_entry(state: dict[str, Any], event: OrchestrationEvent) -> list[dict[str, Any]]:
    logs = list(state.get("execution_logs", []))
    logs.append(event.model_dump(mode="json"))
    return logs
