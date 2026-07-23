import pytest

from providers.image.models import ImageGenerationRequest


def test_image_request_validates_prompt() -> None:
    with pytest.raises(ValueError):
        ImageGenerationRequest(prompt=" ")


def test_image_request_validates_output_format() -> None:
    with pytest.raises(ValueError):
        ImageGenerationRequest(
            prompt="Product image",
            output_format="bmp",
        )
