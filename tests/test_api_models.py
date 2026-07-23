import pytest
from pydantic import ValidationError

from api.models import CreateVideoRequest


def test_create_video_request_validates_mode() -> None:
    with pytest.raises(ValidationError):
        CreateVideoRequest(
            name="Lamp",
            description="Smart lamp",
            target_market="Home workers",
            mode="invalid",
        )


def test_create_video_request_accepts_features() -> None:
    request = CreateVideoRequest(
        name="Lamp",
        description="Smart lamp",
        target_market="Home workers",
        features=["Adaptive light"],
    )

    assert request.features == ["Adaptive light"]
