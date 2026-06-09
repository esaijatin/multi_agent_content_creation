from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AstraOS Orchestrator"
    debug: bool = True

    redis_url: str = "redis://localhost:6379/0"
    orchestrator_internal_api_key: str = "orchestrator-internal-dev-key"

    max_revision_iterations: int = 3
    critique_score_threshold: float = 0.75

    # Ollama
    ollama_base_url: str = Field(default="http://ollama:11434", alias="OLLAMA_BASE_URL")
    ollama_model_planner: str = Field(default="qwen2.5:7b", alias="OLLAMA_MODEL_PLANNER")
    ollama_model_writer: str = Field(default="llama3:8b", alias="OLLAMA_MODEL_WRITER")
    ollama_request_timeout: float = Field(default=120.0, alias="OLLAMA_REQUEST_TIMEOUT")
    ollama_max_retries: int = 3
    ollama_default_temperature: float = 0.4
    ollama_default_max_tokens: int = 4096

    planner_max_retries: int = 3
    writer_max_retries: int = 2

    # Model routing keys (config-driven)
    model_role_planner: str = "planner"
    model_role_writer: str = "writer"


@lru_cache
def get_settings() -> Settings:
    return Settings()
