from datetime import UTC
from pathlib import Path

from core.helpers import (
    ensure_directory,
    generate_id,
    read_json,
    utc_now,
    write_json,
)


def test_utc_now_is_timezone_aware() -> None:
    value = utc_now()

    assert value.tzinfo is UTC


def test_generate_id_with_prefix() -> None:
    value = generate_id("Video Project")

    assert value.startswith("video-project_")
    assert len(value) > len("video-project_")


def test_ensure_directory_creates_nested_path(tmp_path: Path) -> None:
    destination = tmp_path / "one" / "two"

    result = ensure_directory(destination)

    assert result == destination
    assert destination.is_dir()


def test_json_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "data" / "sample.json"
    payload = {"name": "AIVA", "ready": True}

    write_json(path, payload)

    assert read_json(path) == payload
