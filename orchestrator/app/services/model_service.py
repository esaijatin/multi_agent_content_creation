"""Model abstraction layer — all inference flows through here."""

from typing import TypeVar

import structlog
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.services.ollama_provider import OllamaProvider
from app.utils.exceptions import ModelServiceError
from app.utils.json_utils import parse_structured

logger = structlog.get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class ModelService:
    """
    Provider-agnostic model interface.
    Agents must never call Ollama directly.
    """

    def __init__(self, provider: OllamaProvider | None = None) -> None:
        self._provider = provider or OllamaProvider()
        self._settings = get_settings()

    def resolve_model(self, role: str) -> str:
        """Config-driven model routing."""
        routing = {
            self._settings.model_role_planner: self._settings.ollama_model_planner,
            self._settings.model_role_writer: self._settings.ollama_model_writer,
        }
        model = routing.get(role)
        if not model:
            raise ModelServiceError(f"Unknown model role: {role}")
        return model

    async def health_check(self) -> dict:
        return await self._provider.health_check()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def generate(
        self,
        *,
        role: str,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[str, dict[str, int]]:
        model = self.resolve_model(role)
        return await self._provider.generate(
            model=model,
            prompt=prompt,
            system=system,
            temperature=temperature or self._settings.ollama_default_temperature,
            max_tokens=max_tokens or self._settings.ollama_default_max_tokens,
            json_mode=False,
        )

    async def structured_generate(
        self,
        *,
        role: str,
        prompt: str,
        schema: type[T],
        system: str | None = None,
        max_attempts: int | None = None,
        temperature: float | None = None,
    ) -> tuple[T, dict[str, int]]:
        """Generate and validate JSON against a Pydantic schema with retries."""
        settings = self._settings
        model = self.resolve_model(role)
        attempts = max_attempts or settings.planner_max_retries
        total_usage: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0}
        last_error: str | None = None

        schema_json = schema.model_json_schema()
        system_prompt = system or "You are a precise structured-output assistant."
        system_prompt += (
            "\nRespond with valid JSON only matching this schema:\n"
            f"{schema_json}"
        )

        for attempt in range(1, attempts + 1):
            try:
                text, usage = await self._provider.generate(
                    model=model,
                    prompt=prompt,
                    system=system_prompt,
                    temperature=temperature or settings.ollama_default_temperature,
                    max_tokens=settings.ollama_default_max_tokens,
                    json_mode=True,
                )
                for k, v in usage.items():
                    total_usage[k] = total_usage.get(k, 0) + v
                parsed = parse_structured(schema, text)
                return parsed, total_usage
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "structured_generate_retry",
                    role=role,
                    attempt=attempt,
                    error=last_error,
                )

        raise ModelServiceError(
            f"Failed to produce valid {schema.__name__} after {attempts} attempts: {last_error}"
        )


_model_service: ModelService | None = None


def get_model_service() -> ModelService:
    global _model_service
    if _model_service is None:
        _model_service = ModelService()
    return _model_service
