from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    environment: str = "development"
    log_level: str = "INFO"
    llm_provider: str = "openai"
    openai_api_key: str | None = None

    @classmethod
    def from_env(cls, env_file: str | Path = ".env") -> Settings:
        load_dotenv(dotenv_path=env_file, override=False)

        return cls(
            environment=os.getenv("AIVA_ENVIRONMENT", "development").strip(),
            log_level=os.getenv("AIVA_LOG_LEVEL", "INFO").strip().upper(),
            llm_provider=os.getenv("AIVA_LLM_PROVIDER", "openai").strip().lower(),
            openai_api_key=_optional_env("OPENAI_API_KEY"),
        )


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None

    value = value.strip()
    return value or None
