from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(UTC)


def utc_now_iso() -> str:
    """Return the current UTC time in ISO 8601 format."""
    return utc_now().isoformat()


def generate_id(prefix: str | None = None) -> str:
    """Generate a compact unique identifier with an optional prefix."""
    value = uuid4().hex
    if prefix is None:
        return value

    normalized_prefix = prefix.strip().lower().replace(" ", "-")
    if not normalized_prefix:
        return value

    return f"{normalized_prefix}_{value}"


def ensure_directory(path: str | Path) -> Path:
    """Create a directory, including its parents, and return its Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_json(
    path: str | Path,
    data: Any,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> Path:
    """Write JSON data atomically and return the destination path."""
    destination = Path(path)
    ensure_directory(destination.parent)

    temporary_path = destination.with_suffix(f"{destination.suffix}.tmp")
    temporary_path.write_text(
        json.dumps(
            data,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=_json_default,
        ),
        encoding="utf-8",
    )
    temporary_path.replace(destination)
    return destination


def read_json(path: str | Path) -> Any:
    """Read and deserialize a UTF-8 JSON file."""
    source = Path(path)
    with source.open("r", encoding="utf-8") as file:
        return json.load(file)


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
