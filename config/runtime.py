from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    openai_api_key: str | None
    llm_model: str
    image_model: str
    voice_model: str
    voice_name: str
    ffmpeg_path: str
    output_root: Path

    @classmethod
    def from_env(cls, env_file: str | Path = ".env") -> RuntimeConfig:
        load_dotenv(env_file, override=False)
        return cls(
            openai_api_key=_optional("OPENAI_API_KEY"),
            llm_model=os.getenv("AIVA_LLM_MODEL", "gpt-5").strip(),
            image_model=os.getenv(
                "AIVA_IMAGE_MODEL",
                "gpt-image-1",
            ).strip(),
            voice_model=os.getenv(
                "AIVA_VOICE_MODEL",
                "gpt-4o-mini-tts",
            ).strip(),
            voice_name=os.getenv(
                "AIVA_VOICE_NAME",
                "alloy",
            ).strip(),
            ffmpeg_path=os.getenv("FFMPEG_PATH", "ffmpeg").strip(),
            output_root=Path(
                os.getenv("AIVA_OUTPUT_ROOT", "output").strip()
            ),
        )

    def validate_real_mode(self) -> None:
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for real provider mode."
            )


def _optional(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
