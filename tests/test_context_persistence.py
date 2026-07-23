from engine.context import WorkflowContext
from schemas.video_planning import ProductInput
from services.context_persistence import (
    load_context,
    save_context,
)


def test_context_round_trip_restores_product_input(tmp_path) -> None:
    context = WorkflowContext(
        project_id="video-1",
        data={
            "product_input": ProductInput(
                name="Smart Lamp",
                description="Adaptive light",
                target_market="Home workers",
                features=("Brightness",),
            )
        },
    )
    path = save_context(context, tmp_path / "context.json")

    restored = load_context(path)

    product = restored.require("product_input")
    assert isinstance(product, ProductInput)
    assert product.name == "Smart Lamp"
