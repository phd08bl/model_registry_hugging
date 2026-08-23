from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime settings. All defaults are safe for a local demonstration."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AIRO Agentic Risk Triage Demo"
    app_env: str = "development"

    llm_mode: str = "ollama"
    allow_mock_fallback: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: float = 120.0
    openai_api_key: SecretStr | None = None
    openai_model: str = ""
    openai_base_url: str | None = None
    openai_timeout_seconds: float = 120.0
    openai_store_responses: bool = False

    case_db_path: str = "data/cases.db"
    checkpoint_db_path: str = "data/checkpoints.db"
    default_autonomy_profile: str = "human_governed"

    @property
    def absolute_case_db_path(self) -> Path:
        path = Path(self.case_db_path)
        return path if path.is_absolute() else PROJECT_ROOT / path

    @property
    def absolute_checkpoint_db_path(self) -> Path:
        path = Path(self.checkpoint_db_path)
        return path if path.is_absolute() else PROJECT_ROOT / path


@lru_cache
def get_settings() -> Settings:
    return Settings()
