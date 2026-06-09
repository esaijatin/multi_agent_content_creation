from functools import lru_cache
from typing import List

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AstraOS"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = ["http://localhost:3000"]
    

    jwt_secret_key: str = Field(
        default="dev-only-change-in-production-32chars!!",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    database_url: PostgresDsn = "postgresql+asyncpg://astraos:astraos_dev_password@localhost:5432/astraos"
    redis_url: RedisDsn = "redis://localhost:6379/0"

    orchestrator_url: str = "http://localhost:8001"
    orchestrator_internal_api_key: str = "orchestrator-internal-dev-key"

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, list):
            return v
        return [origin.strip() for origin in str(v).split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
