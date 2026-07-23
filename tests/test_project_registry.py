from services.project_registry import list_projects
from storage.checkpoints import CheckpointStore, PipelineStage


def test_project_registry_lists_saved_projects(tmp_path) -> None:
    project = tmp_path / "video-1"
    project.mkdir()
    context_path = project / "context.json"
    context_path.write_text("{}", encoding="utf-8")

    CheckpointStore(project).save(
        project_id="video-1",
        stage=PipelineStage.PLANNED,
        context_path=context_path,
    )

    projects = list_projects(tmp_path)

    assert len(projects) == 1
    assert projects[0].project_id == "video-1"
    assert projects[0].stage == "planned"


def test_project_registry_ignores_unrelated_directories(tmp_path) -> None:
    (tmp_path / "random-folder").mkdir()

    assert list_projects(tmp_path) == ()
