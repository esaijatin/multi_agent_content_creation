from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.routes import router
from app.checkpoints.redis_checkpoint import close_checkpointer, init_checkpointer
from app.services.execution_service import get_execution_service
from app.services.state_manager import close_redis, init_redis

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("orchestrator_starting")
    await init_redis()
    await init_checkpointer()
    recovered = await get_execution_service().recover_interrupted()
    logger.info("orchestrator_recovery_complete", recovered=recovered)
    yield
    await close_checkpointer()
    await close_redis()
    logger.info("orchestrator_stopped")


app = FastAPI(
    title="AstraOS Orchestrator",
    description="LangGraph workflow execution service with Redis checkpointing",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(router)
