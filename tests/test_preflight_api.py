from fastapi.testclient import TestClient

from api.app import create_app


def test_real_preflight_endpoint_returns_checks(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AIVA_OUTPUT_ROOT", str(tmp_path))
    monkeypatch.setattr("shutil.which", lambda executable: None)

    client = TestClient(create_app())
    response = client.get("/api/preflight/real")

    assert response.status_code == 200
    payload = response.json()
    assert payload["passed"] is False
    assert len(payload["checks"]) == 4
