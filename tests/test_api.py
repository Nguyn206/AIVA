from fastapi.testclient import TestClient

from api.app import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_projects_endpoint_returns_list(tmp_path) -> None:
    client = TestClient(create_app())

    response = client.get(
        "/api/projects",
        params={"output_root": str(tmp_path)},
    )

    assert response.status_code == 200
    assert response.json() == []
