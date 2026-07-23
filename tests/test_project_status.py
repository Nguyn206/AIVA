from services.project_status import get_project_status
from storage.checkpoints import CheckpointStore, PipelineStage


def test_project_status_reports_checkpoint(tmp_path) -> None:
    project_dir = tmp_path / "video-1"
    project_dir.mkdir()
    context_path = project_dir / "context.json"
    context_path.write_text("{}", encoding="utf-8")

    CheckpointStore(project_dir).save(
        project_id="video-1",
        stage=PipelineStage.IMAGES_GENERATED,
        context_path=context_path,
    )

    status = get_project_status(tmp_path, "video-1")

    assert status.checkpoint_exists is True
    assert status.context_exists is True
    assert status.stage == PipelineStage.IMAGES_GENERATED
