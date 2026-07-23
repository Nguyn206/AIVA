from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Final

from core.constants import DEFAULT_LOG_LEVEL, LOG_DIR
from core.helpers import ensure_directory

_DEFAULT_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
_DEFAULT_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    level: str = DEFAULT_LOG_LEVEL,
    *,
    log_to_file: bool = True,
    log_file: str | Path | None = None,
) -> None:
    """Configure console logging and optional rotating file logging."""
    normalized_level = level.upper()
    numeric_level = getattr(logging, normalized_level, logging.INFO)

    formatter = logging.Formatter(
        _DEFAULT_FORMAT,
        datefmt=_DEFAULT_DATE_FORMAT,
    )

    handlers: list[logging.Handler] = []

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    if log_to_file:
        destination = Path(log_file) if log_file else LOG_DIR / "aiva.log"
        ensure_directory(destination.parent)

        file_handler = RotatingFileHandler(
            destination,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
