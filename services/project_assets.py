from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectAsset:
    name: str
    relative_path: str
    size_bytes: int
    asset_type: str


def list_project_assets(
    output_root: str | Path,
    project_id: str,
) -> tuple[ProjectAsset, ...]:
    project_directory = Path(output_root) / project_id
    if not project_directory.is_dir():
        return ()

    assets: list[ProjectAsset] = []

    for path in sorted(project_directory.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(project_directory).as_posix()
        assets.append(
            ProjectAsset(
                name=path.name,
                relative_path=relative_path,
                size_bytes=path.stat().st_size,
                asset_type=_asset_type(path),
            )
        )

    return tuple(assets)


def resolve_project_asset(
    output_root: str | Path,
    project_id: str,
    relative_path: str,
) -> Path:
    project_directory = (Path(output_root) / project_id).resolve()
    candidate = (project_directory / relative_path).resolve()

    try:
        candidate.relative_to(project_directory)
    except ValueError as exc:
        raise ValueError("Asset path escapes the project directory.") from exc

    if not candidate.is_file():
        raise FileNotFoundError(
            f"Project asset not found: {relative_path}"
        )

    return candidate


def _asset_type(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix in {".mp4", ".mov", ".webm", ".mkv"}:
        return "video"
    if suffix in {".mp3", ".wav", ".aac", ".flac", ".opus"}:
        return "audio"
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return "image"
    if suffix in {".srt", ".vtt"}:
        return "subtitle"
    if suffix == ".json":
        return "metadata"

    return "file"
