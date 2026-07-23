from fastapi.testclient import TestClient

from api.app import create_app


def test_download_final_video(tmp_path) -> None:
    project = tmp_path / "video-1"
    project.mkdir()
    (project / "final.mp4").write_bytes(b"video-content")

    client = TestClient(create_app())
    response = client.get(
        "/api/projects/video-1/video",
        params={"output_root": str(tmp_path)},
    )

    assert response.status_code == 200
    assert response.content == b"video-content"


def test_project_assets_endpoint(tmp_path) -> None:
    project = tmp_path / "video-1"
    project.mkdir()
    (project / "final.mp4").write_bytes(b"video-content")

    client = TestClient(create_app())
    response = client.get(
        "/api/projects/video-1/assets",
        params={"output_root": str(tmp_path)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["relative_path"] == "final.mp4"
    assert payload[0]["asset_type"] == "video"
