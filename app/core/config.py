"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Support Ticket Intelligence"
    data_path: Path = Path("data/support_tickets.csv")
    as_of_date: str | None = None
    llm_provider: str = "groq"
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    llm_timeout_seconds: float = 20.0
    max_result_rows: int = Field(default=100, ge=1, le=1000)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings."""

    return Settings()
