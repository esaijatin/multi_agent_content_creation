"""Low-level Ollama HTTP client — not used directly by agents."""

from typing import Any

import httpx
import structlog

from app.config import get_settings
from app.utils.exceptions import ModelServiceError

logger = structlog.get_logger(__name__)


class OllamaProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.timeout = settings.ollama_request_timeout

    async def health_check(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return {"status": "healthy", "models": response.json().get("models", [])}

    async def generate(
        self,
        *,
        model: str,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.4,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> tuple[str, dict[str, int]]:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system
        if json_mode:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
            except httpx.TimeoutException as exc:
                raise ModelServiceError(f"Ollama request timed out: {exc}") from exc
            except httpx.HTTPError as exc:
                raise ModelServiceError(f"Ollama HTTP error: {exc}") from exc

        data = response.json()
        text = data.get("response", "")
        usage = {
            "prompt_tokens": data.get("prompt_eval_count", 0),
            "completion_tokens": data.get("eval_count", 0),
        }
        logger.debug("ollama_generate_complete", model=model, usage=usage)
        return text, usage
