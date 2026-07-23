from storage.checkpoints import (
    CheckpointStore,
    PipelineStage,
)


def test_checkpoint_store_saves_and_loads(tmp_path) -> None:
    store = CheckpointStore(tmp_path)
    context_path = tmp_path / "context.json"

    store.save(
        project_id="video-1",
        stage=PipelineStage.IMAGES_GENERATED,
        context_path=context_path,
    )

    checkpoint = store.load()
    assert checkpoint is not None
    assert checkpoint.project_id == "video-1"
    assert checkpoint.stage == PipelineStage.IMAGES_GENERATED
    assert store.reached(PipelineStage.PLANNED) is True
    assert store.reached(PipelineStage.RENDERED) is False
