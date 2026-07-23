from engine.context import WorkflowContext
from services.project_manifest import write_project_manifest


def test_project_manifest_writes_json(tmp_path) -> None:
    context = WorkflowContext(
        project_id="project-1",
        data={"status": "ready"},
    )

    path = write_project_manifest(
        context,
        tmp_path / "manifest.json",
    )

    assert path.exists()
    assert '"project_id": "project-1"' in path.read_text(
        encoding="utf-8"
    )
