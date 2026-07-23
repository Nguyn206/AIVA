from fastapi.testclient import TestClient

from api.app import create_app


def test_create_video_job_returns_job_id() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/jobs/videos",
        json={
            "name": "Smart Lamp",
            "description": "Adaptive desk lamp",
            "target_market": "Home workers",
            "features": ["Adaptive brightness"],
            "mode": "mock",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["job_id"]
    assert payload["status"] in {"queued", "running"}


def test_missing_job_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/api/jobs/missing-job")

    assert response.status_code == 404
