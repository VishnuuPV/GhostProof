from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="GHOSTPROOF_", extra="ignore")

    env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    ai_service_url: str = "http://localhost:8100"
    inference_mode: str = Field(default="local", pattern="^(local|remote)$")
    database_url: str = "sqlite:///./ghostproof-dev.db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins_raw: str = Field(
        default="http://localhost:3000",
        validation_alias="GHOSTPROOF_CORS_ORIGINS",
    )
    log_level: str = "INFO"
    max_upload_mb: int = 25

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
