from __future__ import annotations

from pathlib import Path
from typing import Final

APP_NAME: Final[str] = "AIVA"
APP_VERSION: Final[str] = "0.1.0"

DEFAULT_ENVIRONMENT: Final[str] = "development"
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
DEFAULT_LLM_PROVIDER: Final[str] = "openai"

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
OUTPUT_DIR: Final[Path] = PROJECT_ROOT / "output"
LOG_DIR: Final[Path] = PROJECT_ROOT / "logs"

SUPPORTED_ENVIRONMENTS: Final[frozenset[str]] = frozenset(
    {"development", "testing", "production"}
)
SUPPORTED_LOG_LEVELS: Final[frozenset[str]] = frozenset(
    {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
)
