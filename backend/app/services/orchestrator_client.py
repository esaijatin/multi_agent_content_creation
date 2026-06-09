from typing import Any
from uuid import UUID

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OrchestratorClient:
    """HTTP client for the LangGraph orchestrator service."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.orchestrator_url.rstrip("/")
        self.api_key = settings.orchestrator_internal_api_key

    def _headers(self) -> dict[str, str]:
        return {
            "X-Internal-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def start_workflow(
        self,
        workflow_id: UUID,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/internal/workflow/start",
                json={"workflow_id": str(workflow_id), "payload": payload},
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()
            logger.info(
                "orchestrator_workflow_queued",
                workflow_id=str(workflow_id),
                thread_id=data.get("thread_id"),
            )
            return data

    async def get_state(self, thread_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/internal/workflow/{thread_id}/state",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def get_events(self, thread_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/internal/workflow/{thread_id}/events",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def approve(self, thread_id: str, approved: bool, feedback: str | None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/internal/workflow/{thread_id}/approve",
                json={"approved": approved, "feedback": feedback},
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def revise(self, thread_id: str, feedback: str, target_stage: str | None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/internal/workflow/{thread_id}/revise",
                json={"feedback": feedback, "target_stage": target_stage},
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()


def get_orchestrator_client() -> OrchestratorClient:
    return OrchestratorClient()
