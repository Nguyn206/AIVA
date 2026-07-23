import pytest

from services.project_assets import (
    list_project_assets,
    resolve_project_asset,
)


def test_project_assets_lists_files(tmp_path) -> None:
    project = tmp_path / "video-1"
    (project / "images").mkdir(parents=True)
    (project / "final.mp4").write_bytes(b"video")
    (project / "images" / "scene.png").write_bytes(b"image")

    assets = list_project_assets(tmp_path, "video-1")

    assert {asset.relative_path for asset in assets} == {
        "final.mp4",
        "images/scene.png",
    }


def test_asset_resolver_prevents_directory_escape(tmp_path) -> None:
    project = tmp_path / "video-1"
    project.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError, match="escapes"):
        resolve_project_asset(
            tmp_path,
            "video-1",
            "../secret.txt",
        )
